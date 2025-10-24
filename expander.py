import asyncio, json, re, datetime
# import asyncpg

def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

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

async def _insert_conversation(conn, title):
    r=await conn.fetchrow("insert into conversations(title) values($1) returning id", title)
    return r["id"]

async def _insert_root(conn, conversation_id, autor, typ, json_data=None, text_data=None):
    r=await conn.fetchrow(
        "insert into conversation_root(conversation_id, autor, type, json_data, text_data) values($1,$2,$3,$4,$5) returning id",
        conversation_id, autor, typ, json.dumps(json_data) if json_data is not None else None, text_data
    )
    return r["id"]

async def _insert_part_json(conn, conversation_id, author, tags, prompt, obj):
    r=await conn.fetchrow(
        "insert into conversation_parts(conversation_id, author, tags, prompt, content_type, content_json) values($1,$2,$3,$4,'json',$5) returning id",
        conversation_id, author, tags, prompt, json.dumps(obj)
    )
    return r["id"]

async def _insert_edge(conn, conversation_id, src_part_id, dst_part_id, label, ordn=0, weight=0):
    await conn.execute(
        "insert into conversation_edges(conversation_id, src_part_id, dst_part_id, label, ord, weight) values($1,$2,$3,$4,$5,$6)",
        conversation_id, src_part_id, dst_part_id, label, ordn, weight
    )


def _sections_to_jobs(screen):
    jobs=[]
    for n in screen.get("nodes",[]):
        if n.get("type")=="section" and "expand" in n:
            spec=n["expand"]
            ins=spec.get("inputs",[])
            enums=[i for i in ins if i.get("type")=="enum" and i.get("options")]
            others=[i for i in ins if i.get("type")!="enum" or not i.get("options")]
            def defv(i):
                t=i.get("type")
                if t=="number": return 30
                if t=="string": return "default"
                if t=="boolean": return True
                return None
            base={i["name"]:defv(i) for i in others}
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
    nxt=screen.get("next",{}) or {}
    for p in (nxt.get("prompts") or []):
        ins=p.get("inputs",[])
        enums=[i for i in ins if i.get("type")=="enum" and i.get("options")]
        others=[i for i in ins if i.get("type")!="enum" or not i.get("options")]
        def defv(i):
            t=i.get("type")
            if t=="number": return 30
            if t=="string": return "default"
            if t=="boolean": return True
            return None
        base={i["name"]:defv(i) for i in others}
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

async def auto_expand(db_dsn, initial_screen, llm, tool_registry=None, title="Auto plan", max_depth=2, fanout=3):
    # conn=await asyncpg.connect(dsn=db_dsn)
    try:
        # conv_id=await _insert_conversation(conn, title)
        # await _insert_root(conn, conv_id, "system", "screen", json_data=initial_screen)
        # root_part_id=await _insert_part_json(conn, conv_id, "assistant", [], None, initial_screen)
        # frontier=[(0,"root",root_part_id,initial_screen)]
        frontier=[(0,"root",1,initial_screen)]
        visited=0
        while frontier:
            depth,label,src_id,screen=frontier.pop(0)
            if depth>=max_depth: 
                continue
            jobs=[]
            jobs+=_sections_to_jobs(screen)
            print("jobs")
            print(jobs)
            jobs+=_prompts_to_jobs(screen)
            jobs+=_tools_to_jobs(screen)
            jobs=jobs[:fanout]
            ordn=0
            for jlabel, payload, meta in jobs:
                if meta.get("source")=="tool" and isinstance(payload,dict):
                    tool_name=payload.get("tool")
                    tool= (tool_registry or {}).get(tool_name)
                    tool_ctx = tool(payload) if tool else {}
                    child=await llm(screen, {"tool_context":tool_ctx,"meta":meta})
                    child_id=await _insert_part_json(conn, conv_id, "assistant", [meta["source"]], json.dumps(payload), child)
                    await _insert_edge(conn, conv_id, src_id, child_id, jlabel, ordn, 1)
                    ordn+=1
                    frontier.append((depth+1,jlabel,child_id,child))
                else:
                    prompt = payload if isinstance(payload,str) else json.dumps(payload)
                    child=await llm(screen, {"prompt":prompt,"meta":meta})
                    child_id=await _insert_part_json(conn, conv_id, "assistant", [meta["source"]], prompt, child)
                    await _insert_edge(conn, conv_id, src_id, child_id, jlabel, ordn, 1)
                    ordn+=1
                    frontier.append((depth+1,jlabel,child_id,child))
                visited+=1
        return conv_id
    finally:
        print("finally")
        # await conn.close()

def expand(initial_screen, tool_registry=None, title="Auto plan", max_depth=3, fanout=3):
    # conv_id=await _insert_conversation(conn, title)
    # await _insert_root(conn, conv_id, "system", "screen", json_data=initial_screen)
    # root_part_id=await _insert_part_json(conn, conv_id, "assistant", [], None, initial_screen)
    # frontier=[(0,"root",root_part_id,initial_screen)]
    frontier=[(0,"root",1,initial_screen)]
    visited=0
    while frontier:
        depth,label,src_id,screen=frontier.pop(0)
        if depth>=max_depth: 
            continue
        jobs=[]
        jobs+=_sections_to_jobs(screen)
        jobs+=_prompts_to_jobs(screen)
        jobs+=_tools_to_jobs(screen)
        print("jobs")
        print(jobs)
        jobs=jobs[:fanout]
        ordn=0
        for jlabel, payload, meta in jobs:
            if meta.get("source")=="tool" and isinstance(payload,dict):
                tool_name=payload.get("tool")
                tool= (tool_registry or {}).get(tool_name)
                tool_ctx = tool(payload) if tool else {}
                child = {"tool_context":tool_ctx,"meta":meta}
                yield child
            else:
                prompt = payload if isinstance(payload,str) else json.dumps(payload)
                child = {"prompt":prompt,"meta":meta}
                yield child
            visited+=1