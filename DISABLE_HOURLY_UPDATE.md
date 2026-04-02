# 禁用每小时自动更新

## 问题
服务器当前在**每小时**自动更新代码并推送到 GitHub，导致本地开发时需要频繁 `git pull`。

## 解决方案

### 方法 1：禁用系统定时器（推荐）

在服务器上执行以下命令：

```bash
# 1. 停止并禁用定时器
sudo systemctl stop ai-update.timer
sudo systemctl disable ai-update.timer

# 2. 检查是否还有其他定时任务
sudo crontab -l | grep -i ai
sudo cat /etc/crontab | grep -i ai
ls /etc/cron.d/ | grep -i ai

# 3. 如果发现有每小时运行的 crontab 条目，删除它
sudo crontab -e
# 删除包含 auto-update.sh 的行
```

### 方法 2：改为仅 GitHub Actions 运行（推荐）

完全禁用服务器本地更新，仅保留 GitHub Actions 每天运行：

```bash
# 在服务器上执行
sudo systemctl stop ai-update.timer
sudo systemctl disable ai-update.timer
sudo rm /etc/systemd/system/ai-update.timer
sudo rm /etc/systemd/system/ai-update.service
sudo systemctl daemon-reload
```

### 方法 3：手动控制更新

保留定时器但改为每周运行：

```bash
# 编辑定时器配置
sudo systemctl edit --full ai-update.timer

# 修改为每周一 3:00 AM
[Timer]
OnCalendar=Mon *-*-* 03:00:00
```

## 验证是否禁用成功

```bash
# 检查定时器状态
sudo systemctl list-timers --all | grep ai-update

# 应该显示为 n/a 或没有输出
```

## 当前配置说明

- **GitHub Actions**: 每天北京时间早上 8:00 (UTC 00:00) 运行
- **服务器 systemd**: 已配置为每天 3:00 AM 运行（但如果每小时运行，说明有其他地方配置错误）

## 手动更新

禁用自动更新后，可以手动运行：

```bash
./auto-update.sh
```
