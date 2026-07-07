# dll-proxy

[![license](https://img.shields.io/github/license/rbxluau/dll-proxy)](https://github.com/rbxluau/dll-proxy/blob/main/LICENSE)

A Python-based DLL proxy toolchain. It generates a proxy DLL that re-exports every symbol from a target DLL and embeds a binary payload that is executed when the proxy is loaded. The proxy source is built with `clang-cl`, and optional OLLVM obfuscation flags can be passed through.

## Credit

This project is inspired by and based on [Flangvik/SharpDllProxy](https://github.com/Flangvik/SharpDllProxy).

## Requirements

- Python 3 with [`pefile`](https://pypi.org/project/pefile/) installed
- `clang-cl` available on `PATH`
- A target DLL whose exports you want to proxy
- A raw binary payload to embed and execute on load

## Usage

```
python main.py -d <path/to/target.dll> -b <path/to/payload.bin> [-o "<ollvm flags>"]
```

- `-d`, `--dll` ¡ª Path to the target DLL. Its exports are forwarded by the generated proxy.
- `-b`, `--bin` ¡ª Path to the binary payload that will be embedded and executed in `DllMain` on `DLL_PROCESS_ATTACH`.
- `-o`, `--ollvm` ¡ª Optional. Pass OLLVM flags to `clang-cl`. When provided without a value, a default set of obfuscation passes is enabled (control-flow flattening, bogus control flow, string encryption, instruction substitution, etc.). You can also supply your own flags, e.g. `-o "-mllvm -fla -mllvm -bcf"`.

The generated source is written to `build/<dll-stem>.cpp` and compiled into `build/<dll-name>`.

## How It Works

1. `main.py` parses the target DLL with `pefile` and emits one `#pragma comment(linker, "/export:...")` line per exported symbol, following the `name=proxy.name,@ordinal` (or `NONAME`) forwarding pattern.
2. The pragma block is substituted into `dllmain.cpp`, alongside the payload bytes formatted as a C byte string.
3. The resulting source is compiled with `clang-cl /LD` (plus any OLLVM flags) to produce the proxy DLL.
4. At runtime, `DllMain` allocates `PAGE_READWRITE` memory, copies the embedded payload into it, changes the protection to `PAGE_EXECUTE_READ`, and runs it on a new thread.

## License

See [LICENSE](https://github.com/rbxluau/dll-proxy/blob/main/LICENSE).
