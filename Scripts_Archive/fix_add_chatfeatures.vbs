Dim fso, f, content, oldStr, newStr
Set fso = CreateObject("Scripting.FileSystemObject")
Set f = fso.OpenTextFile("c:\Users\Administrator\Desktop\111\index.html", 1, False, -1)
content = f.ReadAll
f.Close

oldStr = "  <script src=""js/main.js""></script>"
newStr = "  <script src=""js/main.js""></script>" & vbCrLf & "  <script src=""js/chat-features.js""></script>"

If InStr(content, oldStr) > 0 Then
    content = Replace(content, oldStr, newStr, 1, 1)
    Set f = fso.OpenTextFile("c:\Users\Administrator\Desktop\111\index.html", 2, False, -1)
    f.Write content
    f.Close
    WScript.Echo "SUCCESS: chat-features.js added"
Else
    WScript.Echo "ERROR: target string not found"
End If
