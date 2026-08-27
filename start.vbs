Set WshShell = CreateObject("WScript.Shell")

' 1. 清理 8000 端口旧进程
WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %a", 0, True

' 2. 静默拉起 FastAPI 后端服务
WshShell.Run "cmd /c python -m uvicorn rag_service:app --reload --port 8000", 0, False

' 3. 立即打开前端页面（不再在后台死等，直接由前端的加载蒙层接管等待状态）
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.Run """" & scriptPath & "\index.html""", 1, False