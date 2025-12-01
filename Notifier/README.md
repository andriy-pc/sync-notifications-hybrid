# Notifier

A lightweight Windows command‑line utility for displaying Windows toast notifications. 
This tool uses the Windows App SDK to show native Windows notifications with a custom title and message.

---

## 📌 Overview

The **Notifier** project is a simple executable that triggers a Windows toast notification using:

* **.NET 10** (Windows)
* **Windows App SDK 1.8**

You can call the program from scripts, schedulers, or other applications that need to display notifications.

Example usage:

```sh
notify.exe "Task Complete" "Your background job has finished."
```

---

## 🚀 Usage

Run the executable with two arguments:

```
notify.exe <title> <message>
```

If required arguments are missing, the program prints:

```
Usage: notify.exe <title> <message>
```

---

## 📦 Requirements

Before building this project, ensure you have the following installed:

### **1. .NET SDK 10.0 (or later)**

Required to build and publish the project targeting:

```
net10.0-windows10.0.26100.0
```

### **2. Windows 10/11**

This project uses Windows-specific APIs and the Windows App SDK.
It **cannot** run on Linux or macOS.

### **3. Windows App SDK Runtime (optional)**

Not required during build, but may be required on machines running the app unless you publish as **self‑contained**.
---

## 🛠 Build Instructions

This project targets **Windows only** because it uses Windows‑specific notification APIs.

### 1. Restore packages

```
dotnet restore
```

### 2. Build normally

```
dotnet build -c Release
```

The compiled output will appear in:

```
bin/Release/net10.0-windows10.0.26100.0/
```

---

## 📦 Publish a Standalone Executable

To distribute a **fully self-contained single executable** (one file that can be moved anywhere and run without additional folders), publish using this PowerShell command:

```powershell
dotnet publish -c Release -r win-x64 `
  -p:PublishSingleFile=true `
  -p:SelfContained=true `
  -p:IncludeAllContentForSelfExtract=true `
  -p:IncludeNativeLibrariesForSelfExtract=true `
  -p:PublishTrimmed=false
```

This produces a large standalone `Notifier.exe` inside:

```
bin/Release/net10.0-windows10.0.26100.0/win-x64/publish/
```

You can move this EXE to **any folder** and it will run without requiring the Windows App SDK runtime to be installed.

---

## 📦 Alternative (Framework-Dependent Single File)

If you prefer a smaller EXE that depends on the system .NET runtime, use:

```powershell
dotnet publish -c Release -r win-x64 `
  -p:PublishSingleFile=true `
  -p:IncludeAllContentForSelfExtract=true `
  -p:PublishTrimmed=false
```

This version is smaller but **must remain inside its publish folder** or may require additional system components.

You can choose the option that best fits your distribution needs.

---

## 📄 Project Structure

```
Notifier.csproj   → .NET project file
notify.cs         → Main program that constructs and sends a toast notification
```

---

## ✅ Features

* Native Windows toast notifications
* Simple command‑line interface
* Stand‑alone executable publishing support
* Uses Windows App SDK modern APIs

---
