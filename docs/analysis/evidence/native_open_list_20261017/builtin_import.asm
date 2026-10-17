
mxmain.dll:     file format pei-i386


Disassembly of section .text:

0052e550 <.text+0x12d550>:
  52e550:	e8 6b b9 fb ff       	call   0x4e9ec0
  52e555:	85 c0                	test   eax,eax
  52e557:	74 02                	je     0x52e55b
  52e559:	ff 00                	inc    DWORD PTR [eax]
  52e55b:	c3                   	ret
  52e55c:	cc                   	int3
  52e55d:	cc                   	int3
  52e55e:	cc                   	int3
  52e55f:	cc                   	int3
  52e560:	55                   	push   ebp
  52e561:	8b ec                	mov    ebp,esp
  52e563:	83 ec 14             	sub    esp,0x14
  52e566:	8d 45 fc             	lea    eax,[ebp-0x4]
  52e569:	c7 45 f0 00 00 00 00 	mov    DWORD PTR [ebp-0x10],0x0
  52e570:	50                   	push   eax
  52e571:	8d 45 f8             	lea    eax,[ebp-0x8]
  52e574:	c7 45 f4 00 00 00 00 	mov    DWORD PTR [ebp-0xc],0x0
  52e57b:	50                   	push   eax
  52e57c:	8d 45 f4             	lea    eax,[ebp-0xc]
  52e57f:	c7 45 f8 00 00 00 00 	mov    DWORD PTR [ebp-0x8],0x0
  52e586:	50                   	push   eax
  52e587:	8d 45 f0             	lea    eax,[ebp-0x10]
  52e58a:	c7 45 fc ff ff ff ff 	mov    DWORD PTR [ebp-0x4],0xffffffff
  52e591:	50                   	push   eax
  52e592:	8d 45 ec             	lea    eax,[ebp-0x14]
  52e595:	50                   	push   eax
  52e596:	68 0c 72 7f 00       	push   0x7f720c
  52e59b:	68 cc 9f 6c 00       	push   0x6c9fcc
  52e5a0:	ff 75 10             	push   DWORD PTR [ebp+0x10]
  52e5a3:	ff 75 0c             	push   DWORD PTR [ebp+0xc]
  52e5a6:	e8 d5 37 fb ff       	call   0x4e1d80
  52e5ab:	83 c4 24             	add    esp,0x24
  52e5ae:	85 c0                	test   eax,eax
  52e5b0:	75 04                	jne    0x52e5b6
  52e5b2:	8b e5                	mov    esp,ebp
  52e5b4:	5d                   	pop    ebp
  52e5b5:	c3                   	ret
  52e5b6:	ff 75 fc             	push   DWORD PTR [ebp-0x4]
  52e5b9:	ff 75 f8             	push   DWORD PTR [ebp-0x8]
  52e5bc:	ff 75 f4             	push   DWORD PTR [ebp-0xc]
  52e5bf:	ff 75 f0             	push   DWORD PTR [ebp-0x10]
  52e5c2:	ff 75 ec             	push   DWORD PTR [ebp-0x14]
  52e5c5:	e8 a6 fe fb ff       	call   0x4ee470
  52e5ca:	83 c4 14             	add    esp,0x14
  52e5cd:	8b e5                	mov    esp,ebp
  52e5cf:	5d                   	pop    ebp
  52e5d0:	c3                   	ret
