---
layout: home
title: nanoMuse docs
hero:
  text: An open-source personal agent for every device you own.
  tagline: One agent on your phone, your computer and the web, one account across them. It does things instead of answering questions, keeps going when the app is closed, remembers you in files you can read, and asks before anything you could not undo. The whole set is one repository under GPL-3.0-or-later, and the same relay runs on a server of yours.
  actions:
    - theme: brand
      text: Install
      link: /android
    - theme: alt
      text: Run it yourself
      link: /self-hosting
    - theme: alt
      text: GitHub
      link: https://github.com/zeeshanhaque21/nanoMuse
    - theme: alt
      text: Paper
      link: https://arxiv.org/abs/2610.08699
---

## Install

| | |
|---|---|
| **Android** 8.0+, arm64 | [nanoMuse-0.1.41-arm64.apk](https://github.com/zeeshanhaque21/nanoMuse/releases/download/v0.1.41/nanoMuse-0.1.41-arm64.apk) · [how to install](/android) |
| **iPhone / iPad** | [TestFlight](https://testflight.apple.com/join/ZHexbDqc) — a beta; the link delivers the build once Apple's beta review has passed · [iOS](/ios) |
| **macOS** 12+ | [Apple Silicon](https://github.com/zeeshanhaque21/nanoMuse/releases/download/v0.1.41/nanoMuse-Desktop-0.1.41-mac-arm64.dmg) · [Intel](https://github.com/zeeshanhaque21/nanoMuse/releases/download/v0.1.41/nanoMuse-Desktop-0.1.41-mac-x64.dmg) · [the desktop app](/desktop) |
| **Windows** 10+ | [nanoMuse-Desktop-0.1.41-win-x64.exe](https://github.com/zeeshanhaque21/nanoMuse/releases/download/v0.1.41/nanoMuse-Desktop-0.1.41-win-x64.exe) |
| **Linux** x64 | [AppImage](https://github.com/zeeshanhaque21/nanoMuse/releases/download/v0.1.41/nanoMuse-Desktop-0.1.41-linux-x64.AppImage) · [.deb](https://github.com/zeeshanhaque21/nanoMuse/releases/download/v0.1.41/nanoMuse-Desktop-0.1.41-linux-x64.deb) · [tar.gz](https://github.com/zeeshanhaque21/nanoMuse/releases/download/v0.1.41/nanoMuse-Desktop-0.1.41-linux-x64.tar.gz) |
| **Docker** | `bash scripts/self-host.sh --local` for your own relay; `docker compose up -d app` for the web app · [run it yourself](/self-hosting) |

Every download is on the [latest release](https://github.com/zeeshanhaque21/nanoMuse/releases/latest).

[What changed in 0.1.41 Choice](https://github.com/zeeshanhaque21/nanoMuse/releases/tag/v0.1.41) · [What each client can do](/parity) · [Where to start contributing](/roadmap) · [What the relay keeps](/privacy) · [What stays on a phone, and whose it is](/sync)

## The film

74 seconds: what nanoMuse does on your phone, your computer and the web..

## Citation

The report *nanoMuse: An Open-Source Personal Agent for Every Device You Own* is on arXiv as [2610.08699](https://arxiv.org/abs/2610.08699): what a personal agent is, how Muse is built, and how nanoMuse answers it in the open. If you find nanoMuse useful, please cite the paper.

```bibtex
@misc{liu2026nanomuseopensourcepersonalagent,
      title={nanoMuse: An Open-Source Personal Agent for Every Device You Own}, 
      author={Guangyi Liu and Yong Liu and Jiangning Zhang},
      year={2026},
      eprint={2610.08699},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2610.08699}, 
}
```
