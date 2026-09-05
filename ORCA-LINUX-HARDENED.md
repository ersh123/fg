# Orca Linux Hardened 26.9.5-hardened.3

Готовая Linux-only сборка Orca для Debian/Ubuntu `amd64`.

## Установка

```bash
wget https://github.com/ersh123/fg/releases/download/orca-linux-hardened-v26.9.5-hardened.3/orca-ide_26.9.5-hardened.3_amd64.deb
echo "668903d0dfa5bfcd87e14d21dc04417d39e3a7b1509f0d307b1b21734511a28c  orca-ide_26.9.5-hardened.3_amd64.deb" | sha256sum -c -
sudo apt install ./orca-ide_26.9.5-hardened.3_amd64.deb
orca-hardened-desktop
```

## Ссылки

- [GitHub Release](https://github.com/ersh123/fg/releases/tag/orca-linux-hardened-v26.9.5-hardened.3)
- [Скачать DEB напрямую](https://github.com/ersh123/fg/releases/download/orca-linux-hardened-v26.9.5-hardened.3/orca-ide_26.9.5-hardened.3_amd64.deb)
- [Полные исходники](https://github.com/ersh123/fg/tree/orca-linux-hardened-source)
- [Hardening CI и воспроизводимая сборка](https://github.com/ersh123/fg/tree/orca-hardening-ci)

## Проверенная идентичность

```text
version=26.9.5-hardened.3
platform=linux
architecture=amd64
package=deb
source_commit=864364aaf356061ed7922a3ec5e00dacd780e3f4
upstream_commit=67e22345daf882190911355eed152ef33e051c5e
verified_build_run=33943045541
deb_size_bytes=162303672
deb_sha256=668903d0dfa5bfcd87e14d21dc04417d39e3a7b1509f0d307b1b21734511a28c
```

## Что усилено

- descendant-aware закрытие процессов для агентов, запущенных вручную внутри обычного терминала;
- Linux admission governor до создания PTY: лимиты терминалов, агентов, параллельных запусков и памяти через `MemAvailable`;
- автоматический ownership-aware release завершённых orchestration workers;
- запуск рабочего стола через transient user-systemd scope с лимитами памяти, swap и числа процессов;
- публикация только в формате `.deb`; AppImage и RPM намеренно исключены.

Пакет прошёл критические регрессионные тесты, Node typecheck, проверку качества изменённого кода, Electron-сборку, проверку содержимого DEB, packaged CLI smoke, реальную установку через `apt`, проверку launcher, удаление пакета и проверку очистки.
