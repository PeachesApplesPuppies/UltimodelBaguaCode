"""Self-contained compressed-Python zipapp entry point for AutoDepth Live."""
import sys


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python AutoDepthLive_v0.4.pyz <serve|play|read|verify|inspect|break|encode|decode|plan|runner|checkpoint> ...')
    action = sys.argv[1]
    if action == 'checkpoint':
        from closed_state import cli
        del sys.argv[1]
        raise SystemExit(cli())
    if action == 'runner':
        from breakable_runner import cli
        del sys.argv[1]
        raise SystemExit(cli())
    if action in ('encode', 'decode', 'plan'):
        from autodepth_hex import main as run
        raise SystemExit(run())
    if action in ('serve','play','read','verify','inspect','break'):
        from autodepth_live import cli
        cli()
        return
    raise SystemExit(f'Unrecognized action: {action}')


if __name__ == '__main__':
    main()
