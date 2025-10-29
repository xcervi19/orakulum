import asyncio, json, re, datetime, hashlib

def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def _hash(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _default_value(spec, opt):
    t=spec["type"]
    if t=="enum": return opt
    if t=="number": return 30
    if t=="string": return "default"
    if t=="boolean": return True
    return None

def _fill_template(tpl, inputs):
    def rep(m):
        k=m.group(1)
        return str(inputs.get(k,""))
    return re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", rep, tpl)

def _ctx_vars(screen):
    v=((screen.get("next") or {}).get("llm_context") or {}).get("variables") or {}
    out={}
    for k,val in v.items():
        if isinstance(val,(dict,list)):
            out[k]=json.dumps(val, ensure_ascii=False)
        else:
            out[k]=str(val)
    return out

def _recent_hashes(screen):
    v=((screen.get("next") or {}).get("llm_context") or {}).get("variables") or {}
    arr=v.get("recent_spans_sha256_json") or []
    return set(arr if isinstance(arr,list) else [])

def _sections_to_jobs(screen):
    jobs=[]
    ctx=_ctx_vars(screen)
    for n in screen.get("nodes",[]):
        if n.get("type")=="section" and "expand" in n:
            spec=n["expand"]
            ins=spec.get("inputs",[]) or []
            enums=[i for i in ins if i.get("type")=="enum" and i.get("options")]
            others=[i for i in ins if i.get("type")!="enum" or not i.get("options")]
            base={i["name"]:_default_value(i,None) for i in others}
            base.update(ctx)
            if enums:
                from itertools import product
                for combo in product(*[e["options"] for e in enums]):
                    inputs=base.copy()
                    for e,v in zip(enums,combo): inputs[e["name"]]=v
                    prompt=_fill_template(spec["prompt_template"], inputs)
                    jobs.append((f"section:{n.get('id','section')}:{':'.join(map(str,combo))}", prompt, {"source":"section","section_id":n.get("id"),"inputs":inputs,"options":list(combo)}))
            else:
                inputs=base
                prompt=_fill_template(spec["prompt_template"], inputs)
                jobs.append((f"section:{n.get('id','section')}", prompt, {"source":"section","section_id":n.get("id"),"inputs":inputs,"options":[]}))
    return jobs

def _prompts_to_jobs(screen):
    jobs=[]
    ctx=_ctx_vars(screen)
    nxt=screen.get("next",{}) or {}
    for p in (nxt.get("prompts") or []):
        ins=p.get("inputs",[]) or []
        enums=[i for i in ins if i.get("type")=="enum" and i.get("options")]
        others=[i for i in ins if i.get("type")!="enum" or not i.get("options")]
        base={i["name"]:_default_value(i,None) for i in others}
        base.update(ctx)
        if enums:
            from itertools import product
            for combo in product(*[e["options"] for e in enums]):
                inputs=base.copy()
                for e,v in zip(enums,combo): inputs[e["name"]]=v
                prompt=_fill_template(p["template"], inputs)
                jobs.append((f"prompt:{p.get('id','prompt')}:{':'.join(map(str,combo))}", prompt, {"source":"prompt","prompt_id":p.get("id"),"inputs":inputs,"options":list(combo)}))
        else:
            inputs=base
            prompt=_fill_template(p["template"], inputs)
            jobs.append((f"prompt:{p.get('id','prompt')}", prompt, {"source":"prompt","prompt_id":p.get("id"),"inputs":inputs,"options":[]}))
    return jobs

def _tools_to_jobs(screen):
    jobs=[]
    for n in screen.get("nodes",[]):
        if n.get("type")=="card":
            for a in n.get("actions",[]) or []:
                if a.get("kind")=="run_tool":
                    jobs.append(("tool:"+a["id"], a["payload"], {"source":"tool","action_id":a["id"]}))
    return jobs

def expand(initial_screen, tool_registry=None, title="Auto plan", max_depth=3, fanout=3):
    frontier=[(0,"root",1,initial_screen)]
    visited=0
    global_recent=_recent_hashes(initial_screen)
    while frontier:
        depth,label,src_id,screen=frontier.pop(0)
        if depth>=max_depth:
            continue
        jobs=[]
        jobs+=_sections_to_jobs(screen)
        jobs+=_prompts_to_jobs(screen)
        jobs+=_tools_to_jobs(screen)
        jobs=jobs[:fanout]
        for jlabel, payload, meta in jobs:
            if meta.get("source")=="tool" and isinstance(payload,dict):
                tool_name=payload.get("tool")
                tool=(tool_registry or {}).get(tool_name)
                tool_ctx=tool(payload) if tool else {}
                child={"tool_context":tool_ctx,"meta":meta}
                yield child
            else:
                prompt=payload if isinstance(payload,str) else json.dumps(payload, ensure_ascii=False)
                h=_hash(prompt)
                if h in global_recent:
                    continue
                global_recent.add(h)
                meta["hash"]=h
                child={"prompt":prompt,"meta":meta}
                yield child
            visited+=1


def extract_context(response: dict) -> dict:
    llm_ctx = response.get("next", {}).get("llm_context", {})
    variables = llm_ctx.get("variables", {})

    summary = llm_ctx.get("conversation_summary", "")
    trace_id = variables.get("trace_id", "")
    targets = variables.get("targetcompanies", "")
    role = variables.get("dreamrole", "")
    client_input = variables.get("clientinput", "")

    return {
        "summary": summary,
        "trace_id": trace_id,
        "targets": targets,
        "role": role,
        "client_input": client_input
    }


def expand(previous_response: dict, summary: str, trace_id: str, targets: str, role: str, client_input: str):
    node_id = previous_response["nodes"][0]["id"] if "nodes" in previous_response else previous_response.get("parent_path_id", "root")
    expand_prompt = """
Vrať striktně JSON pouze {"delta_nodes": Element[]}.
{"delta_nodes": Element[]} generuj pro vytvoreni webove stranky. 
Elementy musí tvořit plnohodnotný edukační obsah. Elementy jsou podcasty edukačního plánu.
Nepoužívej callouty pro doplňování informací. Uživatel musí informace číst a vstřebávat.
Obsah musí být virální, inspirativní a dopaminový.
Bez časových rámců. Styl osobního mentora, dopaminový.
Musíš navazovat na **conversation_summary**.
Pokud je **expand_mode = depth**, navazuj na **conversation_summary** a generuj další uzly.
Pokud je **expand_mode = width**, navazuj na **conversation_summary** a generuj další edukační texty a kódy.
Texty musí čtenáře připravovat na pohovory a další kariérní růst.
Cílem generování je konkurovat knize *“How to Crack the Coding Interview”*, ale obsah musí být rychlý, úderný a vyvolávat dojem důležitosti.
Pokud je **expand_mode = width**, podle **conversation_summary** generuj nová témata o tom, jak obstát na technickém pohovoru.
Neopakuj informace z **conversation_summary** – doplňuj nová témata a nápady.


Element =
| { "type": "heading", "level": "h1"|"h2"|"h3", "text": string }
| { "type": "text", "text": string }
| { "type": "bullets", "items": string[] }
| { "type": "code", "lang": "ts"|"js"|"py"|"bash", "lines": string[] }
| { "type": "callout", "style": "info"|"warn"|"success"|"emphasis", "text": string }
| { "type": "stat", "label": string, "value": string }
| { "type": "metric", "label": string, "value": string, "trend": "up"|"down"|"flat" }
| { "type": "badge", "text": string }
| { "type": "quote", "text": string, "source"?: string }
| { "type": "divider" }

"""

    expand_input = f"""
conversation_summary: "{summary}"
trace_id: "{trace_id}"
parent_path_id: "{node_id}"
expand_mode: depth
targetcompanies: "{targets}"
dreamrole: "{role}"
clientinput: "{client_input}"
"""

    return {
        "setup": expand_prompt.strip(),
        "input": expand_input.strip(),
        "context": {
            "trace_id": trace_id,
            "parent_path_id": node_id,
            "expand_mode": "depth",
            "targetcompanies": targets,
            "dreamrole": role,
            "clientinput": client_input,
            "conversation_summary": summary
        }
    }

def build_llm_prompt(data: dict) -> str:
    setup = data["setup"].strip()
    input_block = data["input"].strip()

    prompt = f"""{setup}

        INPUT:
        {input_block}
        """
    return prompt.strip()
