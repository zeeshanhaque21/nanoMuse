<p align="center">
  <img src="https://raw.githubusercontent.com/nano-muse/nanoMuse/main/assets/brand/nanomuse-cover.png" alt="nanoMuse: an open-source personal agent for every device you own">
</p>

<p align="center">
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/README.md">English</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_zh.md">简体中文</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_zh-TW.md">繁體中文</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_es.md">Español</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_fr.md">Français</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_id.md">Bahasa Indonesia</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_ja.md">日本語</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_ko.md">한국어</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_ru.md">Русский</a> |
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/docs/readme/README_vi.md">Tiếng Việt</a>
</p>
<p align="center">
  <a href="https://github.com/zeeshanhaque21/nanoMuse/stargazers"><img src="https://img.shields.io/github/stars/nano-muse/nanoMuse?style=flat&label=stars" alt="GitHub stars"></a>
  <a href="https://github.com/zeeshanhaque21/nanoMuse/releases"><img src="https://img.shields.io/github/downloads/nano-muse/nanoMuse/total?label=downloads" alt="Downloads"></a>
  <a href="https://github.com/zeeshanhaque21/nanoMuse/actions/workflows/ci.yml"><img src="https://github.com/zeeshanhaque21/nanoMuse/actions/workflows/ci.yml/badge.svg?branch=main" alt="Test Suite"></a>
  <a href="https://github.com/zeeshanhaque21/nanoMuse/releases"><img src="https://img.shields.io/badge/Fork%20releases-zeeshanhaque21%2FnanoMuse-5B4EE6" alt="Fork releases"></a>
  <a href="https://github.com/zeeshanhaque21/nanoMuse"><img src="https://img.shields.io/badge/Fork-zeeshanhaque21%2FnanoMuse-0a66e4" alt="Fork"></a>
  <a href="https://github.com/zeeshanhaque21/nanoMuse/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nano-muse/nanoMuse?label=license" alt="GPL-3.0-or-later"></a>
  <a href="https://discord.gg/bkTySmm28X"><img src="https://img.shields.io/badge/Discord-join-5865F2?logo=discord&logoColor=white" alt="Discord"></a>
</p>

**nanoMuse is an open-source personal agent for every device you own.** One agent with a name and a look of its own, in the style of Meta's [Muse](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/): it does things instead of answering questions, keeps working while the app is closed, remembers you, and stops to ask before anything you could not undo.

*nano* means the whole set, small enough to run and deploy yourself: the phone app, the desktop app, the web console and the relay that joins them are all in this repository, under GPL-3.0-or-later. **[Free, open source, non-profit. Let's build it together.](CONTRIBUTING.md)** Sign in and you get a free allowance of model use on the community relay (the developer pays for it); when it is gone, [use your own key](docs/own-key.md). The same relay runs on a server of yours, so nothing has to leave your house. Latest: **0.1.41 Choice**, [release notes](https://github.com/zeeshanhaque21/nanoMuse/releases/tag/v0.1.41) · [try it in the browser](https://demo.nanomuse.dev/).

https://github.com/user-attachments/assets/c7694d5a-9450-4f99-9254-5d70560d7565

<p align="center"><a href="https://nanomuse.cn/media/film/nanomuse-film-en-web.mp4">English</a> · <a href="https://nanomuse.cn/media/film/nanomuse-film-zh-web.mp4">中文</a> · <a href="https://nanomuse.cn/#film">nanomuse.cn</a></p>

## 🗞️ News

- `2026-10-07` 📄 Our paper is available on [arXiv](https://arxiv.org/abs/2610.08699).
- `2026-10-07` 🚀 Latest version: [0.1.41 Choice](https://github.com/zeeshanhaque21/nanoMuse/releases/tag/v0.1.41).
- `2026-09-25` 🎉 nanoMuse is released.

Every version: [releases](https://github.com/zeeshanhaque21/nanoMuse/releases).

## Install

This fork ships no hosted demo and no default relay: configure [your own relay](docs/cloud.md) first, then install from [this fork's releases](https://github.com/zeeshanhaque21/nanoMuse/releases/latest) — the Android APK, the desktop app for Windows, macOS and Linux (`nanoMuse-Desktop-<version>-…`), the terminal binary (`nanomuse-desktop-terminal-<version>-…`), or `pipx install "git+https://github.com/zeeshanhaque21/nanoMuse"` with Python 3.11+. Upstream's public site and download mirror are not used by this fork. [docs/desktop.md](docs/desktop.md) and [docs/every-device.md](docs/every-device.md) say how the clients meet. On the phone:

1. Download `nanoMuse-<version>-arm64.apk` from the [latest fork release](https://github.com/zeeshanhaque21/nanoMuse/releases/latest) — Android 8.0 or newer, a 64-bit phone. Verify with `sha256sum -c nanoMuse-<version>-arm64.apk.sha256` if you like.
2. Open it. Android asks once to allow the install; every version is signed with the same key, so updates install over the previous one and keep your data.
3. Connect a model. *Sign in — free*: a phone number (the code comes by SMS) or an e-mail address, and the agent has a free allowance on [nanoMuse Cloud](docs/cloud.md) — no key needed, nothing to pay; the account page says how much is left and how it grows. The chat model is `deepseek-v4.1-flash` and the hands use `qwen3.8-27b`; the two are separate settings. When the allowance is gone, use your own key — [Alibaba Cloud Bailian](docs/own-key.md) in mainland China, [OpenRouter](docs/own-key.md) elsewhere (Bailian does not sign up overseas accounts), any OpenAI-compatible endpoint, or one of the OAuth sign-ins the app ships with. Then, if you like, the two permissions that let the agent use your phone's apps (skippable), and the first conversation, which asks what to call you and lets the agent pick its own name.
4. Optional — *Settings → Image & video models*: an image model (qwen-image-3.0 on Alibaba Cloud Model Studio, gpt-image-1, or any provider with the OpenAI images endpoint) lets the agent change its look and draw pictures; a video model (wan2.2-i2v-flash on Model Studio) makes the look move. Muse has these built in; nanoMuse uses your own, and the agent tells you when one is missing.

All downloads come from the [latest release](https://github.com/zeeshanhaque21/nanoMuse/releases/latest); the same files are on [nanomuse.cn/dl](https://nanomuse.cn/dl/) when GitHub is slow where you are. Open the app, sign in with an e-mail or a mainland-China phone number, and it has a model to think with. The phone, the desktop and the web share one account and show the same conversations.

## What it does

<table>
  <tr>
    <td width="50%" valign="top"><b>Does things.</b><br>A Linux shell, a browser, MCP servers and skills, and, with <i>Hands</i> on, the apps on your phone and the windows on your computer through their screens, for everything that never had an API.</td>
    <td width="50%" valign="top"><b>Asks first.</b><br>A stop before deleting, sending or paying, remembered for once, this chat or always; passwords and codes are yours to type. A login or a CAPTCHA is handed to you, <i>Done</i> resumes.</td>
  </tr>
  <tr>
    <td width="50%" valign="top"><b>Reaches your other devices.</b><br>Say it on the phone, it runs on your PC; <code>@Mac …</code> at the start of a message sends the task there. Approvals come back to the device in your hand.</td>
    <td width="50%" valign="top"><b>Keeps going.</b><br>Goals checked on a schedule, routines that run while the app is closed, a feed written for you each morning.</td>
  </tr>
  <tr>
    <td width="50%" valign="top"><b>Remembers you.</b><br>What it is, what it knows about you and when it wakes are Markdown files you can read and edit.</td>
    <td width="50%" valign="top"><b>Lives in your chat apps.</b><br>It answers in 飞书, 钉钉, 企业微信 and Telegram.</td>
  </tr>
  <tr>
    <td width="50%" valign="top"><b>A look of its own.</b><br>Describe one, your image model draws it, a video model makes it move. A small dragon by default.</td>
    <td width="50%" valign="top"><b>Any model.</b><br>The relay's allowance, your own key at one of eighteen providers (Bailian, OpenRouter, OpenAI, Gemini, DeepSeek and more), or a plan you already pay for: ChatGPT, Claude, Kimi. A provider without picture or video models leaves those two off, and the app says so.</td>
  </tr>
</table>

## How it works

Each device runs its own agent: the phone inside the APK (Alpine Linux under proot, a shell, a browser, MCP), the computer inside nanoMuse Desktop (DeepSeek Harness with the Python runtime for the hands). Signed in, they meet on the relay and can ask each other for things; the text of the conversations travels through it, files and screenshots stay where they were made.

<p align="center">
  <img src="https://raw.githubusercontent.com/nano-muse/nanoMuse/main/assets/brand/devices-loop.png" alt="Android, the desktop (Mac, Windows, Linux), iPhone and iPad, and the web app around one account: the relay signs the devices in and carries the conversation between them" width="92%">
</p>

[docs/every-device.md](docs/every-device.md) explains the devices, [docs/hub.md](docs/hub.md) the frames, [docs/cloud.md](docs/cloud.md) the relay, [docs/privacy.md](docs/privacy.md) what it keeps.

## Compared with Muse and OpenMinis

| | Meta Muse | OpenMinis | nanoMuse |
|---|---|---|---|
| Where the agent runs | A cloud VM per user | The phone it is installed on | Your phone, your computer, or a server of yours, one account across them |
| Apps without an API | Out of reach; the VM never touches your devices | An accessibility CLI on Android | The screen as a hand on the phone and the computer: screenshots, APIs first, you take over for logins. Not on iOS, where the system does not allow it |
| Other devices | Clients of one VM | The one it is installed on | Devices ask each other for things over the hub, with approvals where you are |
| Models | Meta's | Bring your own | The relay's free allowance, or your own |
| Licence | Closed | GPL-3.0 | GPL-3.0-or-later, built on OpenMinis |

## Docs

[nanomuse.cn/docs](https://nanomuse.cn/docs/): install per platform, every device, hands, connectors, memory, self-hosting, the protocols. The sources are in [docs/](docs/); what changed in each version is in the [CHANGELOG](CHANGELOG.md) and [docs/releases/](docs/releases/).

## Self-host

One VPS, one hour: [docs/self-hosting.md](docs/self-hosting.md). Three ways: no server at all with your own key, your own relay with `scripts/self-host.sh`, or a runtime of your own for the web app.

## Contribute

Use it for a real task, report what broke, then pick something focused: [CONTRIBUTING.md](CONTRIBUTING.md) has the setup and the conventions, [AGENTS.md](AGENTS.md) the rules a coding agent follows in this tree, and the [roadmap](docs/roadmap.md) says where to start. [Issues](https://github.com/zeeshanhaque21/nanoMuse/issues) · [Discussions](https://github.com/zeeshanhaque21/nanoMuse/discussions) · [Discord](https://discord.gg/bkTySmm28X).

## ⭐️ Citation

If you find nanoMuse useful, please cite the paper.

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

## Acknowledgements

nanoMuse stands on other people's work; [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) has the terms.

- [OpenMinis](https://github.com/OpenMinis/OpenMinis): the on-device agent the phone app is built on, with [proot](https://github.com/nano-muse/proot) and [Alpine Linux](https://alpinelinux.org/) for the sandbox.
- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness): the agent harness the desktop app is a plugin of.
- [UI-TARS-desktop](https://github.com/bytedance/UI-TARS-desktop) (ByteDance): the desktop hands' operator is a port of theirs, and the stage's markers follow their ScreenMarker.
- [MobileGym](https://github.com/Purewhiter/mobilegym), [MemGUI-Bench](https://github.com/lgy0404/MemGUI-Bench), [PhoneHarness](https://github.com/PhoneHarness/PhoneHarness), [CopilotKit/OpenMuse](https://github.com/CopilotKit/OpenMuse), [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM), [ClawGUI](https://github.com/ZJU-REAL/ClawGUI): the phone operator, the traces and the product ideas.

## Disclaimer

nanoMuse is an independent community project, not affiliated with or endorsed by Meta Platforms, Inc.; Muse is their trademark. The dragon is the project's own.

## License

[GPL-3.0-or-later](LICENSE). The phone app is based on OpenMinis 1.13 (GPL-3.0), modified since 2026-09-24; see [NOTICE](NOTICE). Earlier versions of the Python line were MIT (tag `pre-openminis`).
