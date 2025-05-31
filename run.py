import os
import sys
import subprocess
import signal

def run_application(args):
    """运行应用"""
    print("Starting application...")
    script_path = os.path.join(os.path.dirname(__file__), 'run_fastapi.py')
    # 将参数传递给子进程
    cmd = [sys.executable, script_path] + args
    result = subprocess.run(cmd)
    
    # 检查子进程的退出状态
    if result.returncode != 0:
        print(f"\nApplication exited with non-zero status: {result.returncode}")
        prompt_restart()

def prompt_restart():
    """提示用户是否重启"""
    response = input("Do you want to restart the application? [Y/n]: ").strip().lower()
    if response not in ('n', 'no'):  # 只有明确输入n或no才不重启
        print("Restarting application...")
        main()  # 直接重新调用main函数
    else:
        print("Exiting application...")
        sys.exit(0)

def handle_interrupt(signum, frame):
    """处理中断信号"""
    print("\nReceived interrupt signal (Ctrl+C)")
    prompt_restart()

def main():
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_interrupt)
    
    try:
        # 获取命令行参数（排除脚本名本身）
        args = sys.argv[1:]
        # 运行应用并传递参数
        run_application(args)
    except Exception as e:
        print(f"Unexpected error: {e}")
        prompt_restart()

if __name__ == '__main__':
    main()