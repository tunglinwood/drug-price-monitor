"""
设置每日定时任务
"""
import os
import sys
from pathlib import Path
from crontab import CronTab

def setup_cron_job():
    """设置 cron 定时任务"""
    
    # 获取当前脚本路径
    script_path = Path(__file__).resolve()
    project_dir = script_path.parent
    
    # 创建 cron 任务
    cron = CronTab(user=True)
    
    # 每天凌晨 2 点执行
    job = cron.new(
        command=f"cd {project_dir} && {sys.executable} compound_monitor.py >> compound_monitor.log 2>&1",
        comment="Daily compound monitor update"
    )
    job.hour.on(2)
    job.minute.on(0)
    
    # 写入 cron
    cron.write()
    
    print(f"✅ Cron 任务已设置")
    print(f"📍 项目目录：{project_dir}")
    print(f"⏰ 执行时间：每天凌晨 2:00")
    print(f"📄 日志文件：{project_dir}/compound_monitor.log")
    
    # 显示当前 cron 任务
    print(f"\n当前 cron 任务:")
    for job in cron:
        if "compound_monitor" in str(job):
            print(f"  {job}")


def setup_systemd_timer():
    """设置 systemd timer（Linux 系统）"""
    
    project_dir = Path(__file__).parent.resolve()
    python_exec = sys.executable
    
    # 创建 service 文件
    service_content = f"""[Unit]
Description=Daily Compound Monitor
After=network.target

[Service]
Type=oneshot
User={os.getenv('USER', 'root')}
WorkingDirectory={project_dir}
ExecStart={python_exec} {project_dir}/compound_monitor.py
StandardOutput=append:{project_dir}/compound_monitor.log
StandardError=append:{project_dir}/compound_monitor.log
"""
    
    service_path = Path.home() / ".config" / "systemd" / "user" / "compound-monitor.service"
    service_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(service_path, 'w') as f:
        f.write(service_content)
    
    # 创建 timer 文件
    timer_content = """[Unit]
Description=Run compound monitor daily
Requires=compound-monitor.service

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""
    
    timer_path = Path.home() / ".config" / "systemd" / "user" / "compound-monitor.timer"
    
    with open(timer_path, 'w') as f:
        f.write(timer_content)
    
    print(f"✅ Systemd timer 文件已创建")
    print(f"📍 Service: {service_path}")
    print(f"📍 Timer: {timer_path}")
    print(f"\n请执行以下命令启用:")
    print(f"  systemctl --user daemon-reload")
    print(f"  systemctl --user enable compound-monitor.timer")
    print(f"  systemctl --user start compound-monitor.timer")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "cron":
            setup_cron_job()
        elif sys.argv[1] == "systemd":
            setup_systemd_timer()
        else:
            print("用法：python setup_scheduler.py [cron|systemd]")
    else:
        print("用法：python setup_scheduler.py [cron|systemd]")
        print("\n选项:")
        print("  cron     - 使用 cron (Linux/Mac)")
        print("  systemd  - 使用 systemd timer (Linux)")
