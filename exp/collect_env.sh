#!/usr/bin/env bash
# Snapshot of the server and software environment (taken before and after the experiment).
# usage: bash collect_env.sh <out dir>
set -uo pipefail
source "$(dirname "$0")/common.sh"
D="${1:?usage: bash collect_env.sh <out dir>}"
mkdir -p "$D"
# a new snapshot replaces an old one in the same directory (cap appends). Before 2026-10-08 21:3x KST the files were
# appended to, so results/seq3x3_20261008/env_after_* hold three snapshots in a row (one per run_experiment.sh call)
rm -f "$D"/[0-9][0-9]_*.txt

cap() {   # cap <file> <command...>: save the command line and its output
	local f="$1"; shift
	{ echo "\$ $*"; "$@" 2>&1; echo; } >> "$D/$f"
}

cap 00_date.txt            date -Is
cap 00_date.txt            hostname
cap 01_os.txt              uname -a
cap 01_os.txt              cat /etc/os-release
cap 01_os.txt              cat /proc/version
cap 02_boot.txt            cat /proc/cmdline
cap 02_boot.txt            grep -E '^GRUB_CMDLINE' /etc/default/grub
cap 02_boot.txt            cat /sys/devices/system/cpu/isolated
cap 03_cpu.txt             lscpu
cap 03_cpu.txt             nproc
cap 04_cpufreq.txt         cat /sys/devices/system/cpu/intel_pstate/status /sys/devices/system/cpu/intel_pstate/no_turbo
cap 04_cpufreq.txt         grep -H . /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_driver \
	/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor \
	/sys/devices/system/cpu/cpu[0-9]*/cpufreq/energy_performance_preference \
	/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_min_freq \
	/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_max_freq
cap 05_memory.txt          free -b
cap 05_memory.txt          grep -E 'MemTotal|MemFree|MemAvailable|Hugepages|AnonHugePages' /proc/meminfo
cap 05_memory.txt          cat /sys/kernel/mm/transparent_hugepage/enabled
cap 05_memory.txt          sudo -n cat /proc/iomem
cap 05_memory.txt          bash -c "sudo -n dmesg | grep -iE 'e820|memmap|user-defined' | head -60"
cap 06_platform.txt        grep -H . /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/product_name \
	/sys/class/dmi/id/board_vendor /sys/class/dmi/id/board_name /sys/class/dmi/id/bios_version /sys/class/dmi/id/bios_date
cap 07_versions.txt        fio --version
cap 07_versions.txt        gcc --version
cap 07_versions.txt        make --version
cap 07_versions.txt        python3 --version
cap 07_versions.txt        git --version
cap 07_versions.txt        nvme version
cap 07_versions.txt        dmesg --version
cap 07_versions.txt        bash --version
cap 07_versions.txt        dpkg-query -W fio libaio1t64 nvme-cli make gcc-13 "linux-headers-$(uname -r)" "linux-image-$(uname -r)"
cap 08_nvmevirt_git.txt    git -C "$REPO_DIR" rev-parse HEAD
cap 08_nvmevirt_git.txt    git -C "$REPO_DIR" log --oneline -15
cap 08_nvmevirt_git.txt    git -C "$REPO_DIR" status --porcelain
cap 08_nvmevirt_git.txt    git -C "$REPO_DIR" remote -v
cap 09_block.txt           lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINT
cap 09_block.txt           bash -c 'ls -l /dev/nvme*'
cap 09_block.txt           sudo -n nvme list
cap 10_modules.txt         bash -c "lsmod | grep -E '^(Module|nvmev)'"
cap 10_modules.txt         cat /proc/loadavg
cap 11_kernel_sysctl.txt   sysctl kernel.dmesg_restrict kernel.kptr_restrict kernel.numa_balancing vm.swappiness
echo "environment snapshot -> $D"
