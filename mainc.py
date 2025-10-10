import asyncio, argparse
from pathlib import Path
from playwright.async_api import async_playwright
from config import Settings
from logic import apply_logic, TASKS



def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--headless", action=argparse.BooleanOptionalAction)
    p.add_argument("--url")
    p.add_argument("--profile")
    p.add_argument("--trace", action=argparse.BooleanOptionalAction)
    p.add_argument("--trace-path")
    p.add_argument("--video-dir")
    return p.parse_args()

async def main():
    args=parse_args()
    s=Settings()
    if args.headless is not None: s.headless=args.headless
    if args.url: s.url=args.url
    if args.profile: s.profile=args.profile
    if args.trace is not None: s.trace=args.trace
    if args.trace_path: s.trace_path=args.trace_path
    if args.video_dir: s.video_dir=args.video_dir
    Path(s.profile).mkdir(parents=True, exist_ok=True)
    if s.trace: Path(s.trace_path).parent.mkdir(parents=True, exist_ok=True)
    launch_opts={}
    if s.video_dir: launch_opts["record_video_dir"]=s.video_dir
    async with async_playwright() as p:
        ctx=await p.chromium.launch_persistent_context(user_data_dir=s.profile, channel="chrome", headless=s.headless, viewport={"width":s.width,"height":s.height}, **launch_opts)
        if s.trace: await ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
        page=await ctx.new_page()
        await page.goto(s.url, wait_until="domcontentloaded")
        await apply_logic(page, TASKS)
        if s.trace: await ctx.tracing.stop(path=s.trace_path)
        await ctx.close()

if __name__=="__main__":
    asyncio.run(main())
