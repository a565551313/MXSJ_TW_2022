
mxmain.dll:     file format pei-i386


Disassembly of section .text:

0045d1d0 <.text+0x5c1d0>:
  45d1d0:	55                   	push   ebp
  45d1d1:	8b ec                	mov    ebp,esp
  45d1d3:	6a ff                	push   0xffffffff
  45d1d5:	68 76 37 6a 00       	push   0x6a3776
  45d1da:	64 a1 00 00 00 00    	mov    eax,fs:0x0
  45d1e0:	50                   	push   eax
  45d1e1:	81 ec d0 00 00 00    	sub    esp,0xd0
  45d1e7:	a1 d0 13 82 00       	mov    eax,ds:0x8213d0
  45d1ec:	33 c5                	xor    eax,ebp
  45d1ee:	89 45 f0             	mov    DWORD PTR [ebp-0x10],eax
  45d1f1:	53                   	push   ebx
  45d1f2:	56                   	push   esi
  45d1f3:	57                   	push   edi
  45d1f4:	50                   	push   eax
  45d1f5:	8d 45 f4             	lea    eax,[ebp-0xc]
  45d1f8:	64 a3 00 00 00 00    	mov    fs:0x0,eax
  45d1fe:	8b 45 10             	mov    eax,DWORD PTR [ebp+0x10]
  45d201:	8d 95 48 ff ff ff    	lea    edx,[ebp-0xb8]
  45d207:	8b 4d 0c             	mov    ecx,DWORD PTR [ebp+0xc]
  45d20a:	52                   	push   edx
  45d20b:	8d 95 58 ff ff ff    	lea    edx,[ebp-0xa8]
  45d211:	c7 85 4c ff ff ff 00 	mov    DWORD PTR [ebp-0xb4],0x0
  45d218:	00 00 00 
  45d21b:	52                   	push   edx
  45d21c:	8d 95 54 ff ff ff    	lea    edx,[ebp-0xac]
  45d222:	c7 85 54 ff ff ff 00 	mov    DWORD PTR [ebp-0xac],0x0
  45d229:	00 00 00 
  45d22c:	52                   	push   edx
  45d22d:	8d 95 4c ff ff ff    	lea    edx,[ebp-0xb4]
  45d233:	c7 85 58 ff ff ff 00 	mov    DWORD PTR [ebp-0xa8],0x0
  45d23a:	00 00 00 
  45d23d:	52                   	push   edx
  45d23e:	8d 95 6c ff ff ff    	lea    edx,[ebp-0x94]
  45d244:	c7 85 48 ff ff ff ff 	mov    DWORD PTR [ebp-0xb8],0xffffffff
  45d24b:	ff ff ff 
  45d24e:	52                   	push   edx
  45d24f:	68 64 b8 7d 00       	push   0x7db864
  45d254:	68 b0 30 6b 00       	push   0x6b30b0
  45d259:	50                   	push   eax
  45d25a:	51                   	push   ecx
  45d25b:	e8 20 4b 08 00       	call   0x4e1d80
  45d260:	83 c4 24             	add    esp,0x24
  45d263:	85 c0                	test   eax,eax
  45d265:	0f 84 32 01 00 00    	je     0x45d39d
  45d26b:	e8 90 0e 09 00       	call   0x4ee100
  45d270:	ff b5 6c ff ff ff    	push   DWORD PTR [ebp-0x94]
  45d276:	50                   	push   eax
  45d277:	e8 f4 24 08 00       	call   0x4df770
  45d27c:	83 c4 08             	add    esp,0x8
  45d27f:	85 c0                	test   eax,eax
  45d281:	74 07                	je     0x45d28a
  45d283:	ff 00                	inc    DWORD PTR [eax]
  45d285:	e9 13 01 00 00       	jmp    0x45d39d
  45d28a:	8d 8d 24 ff ff ff    	lea    ecx,[ebp-0xdc]
  45d290:	e8 2b c3 1a 00       	call   0x6095c0
  45d295:	ff b5 6c ff ff ff    	push   DWORD PTR [ebp-0x94]
  45d29b:	8d 85 70 ff ff ff    	lea    eax,[ebp-0x90]
  45d2a1:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [ebp-0x4],0x0
  45d2a8:	68 c4 30 6b 00       	push   0x6b30c4
  45d2ad:	50                   	push   eax
  45d2ae:	e8 21 75 16 00       	call   0x5c47d4
  45d2b3:	83 c4 0c             	add    esp,0xc
  45d2b6:	8d 85 70 ff ff ff    	lea    eax,[ebp-0x90]
  45d2bc:	8d 8d 24 ff ff ff    	lea    ecx,[ebp-0xdc]
  45d2c2:	68 cc 30 6b 00       	push   0x6b30cc
  45d2c7:	50                   	push   eax
  45d2c8:	e8 93 c4 1a 00       	call   0x609760
  45d2cd:	85 c0                	test   eax,eax
  45d2cf:	74 2d                	je     0x45d2fe
  45d2d1:	ff b5 48 ff ff ff    	push   DWORD PTR [ebp-0xb8]
  45d2d7:	ff b5 58 ff ff ff    	push   DWORD PTR [ebp-0xa8]
  45d2dd:	ff b5 54 ff ff ff    	push   DWORD PTR [ebp-0xac]
  45d2e3:	ff b5 4c ff ff ff    	push   DWORD PTR [ebp-0xb4]
  45d2e9:	ff b5 6c ff ff ff    	push   DWORD PTR [ebp-0x94]
  45d2ef:	e8 7c 11 09 00       	call   0x4ee470
  45d2f4:	83 c4 14             	add    esp,0x14
  45d2f7:	8b f0                	mov    esi,eax
  45d2f9:	e9 8b 00 00 00       	jmp    0x45d389
  45d2fe:	ff b5 38 ff ff ff    	push   DWORD PTR [ebp-0xc8]
  45d304:	ff b5 28 ff ff ff    	push   DWORD PTR [ebp-0xd8]
  45d30a:	68 d4 30 6b 00       	push   0x6b30d4
  45d30f:	e8 1c 75 08 00       	call   0x4e4830
  45d314:	8b f0                	mov    esi,eax
  45d316:	56                   	push   esi
  45d317:	e8 34 fe ff ff       	call   0x45d150
  45d31c:	83 c4 10             	add    esp,0x10
  45d31f:	8b d8                	mov    ebx,eax
  45d321:	ff 0e                	dec    DWORD PTR [esi]
  45d323:	89 9d 44 ff ff ff    	mov    DWORD PTR [ebp-0xbc],ebx
  45d329:	75 0c                	jne    0x45d337
  45d32b:	8b 4e 04             	mov    ecx,DWORD PTR [esi+0x4]
  45d32e:	56                   	push   esi
  45d32f:	8b 49 18             	mov    ecx,DWORD PTR [ecx+0x18]
  45d332:	ff d1                	call   ecx
  45d334:	83 c4 04             	add    esp,0x4
  45d337:	85 db                	test   ebx,ebx
  45d339:	74 4c                	je     0x45d387
  45d33b:	8b 43 04             	mov    eax,DWORD PTR [ebx+0x4]
  45d33e:	3d 80 9e 7e 00       	cmp    eax,0x7e9e80
  45d343:	74 12                	je     0x45d357
  45d345:	68 80 9e 7e 00       	push   0x7e9e80
  45d34a:	50                   	push   eax
  45d34b:	e8 b0 5d 07 00       	call   0x4d3100
  45d350:	83 c4 08             	add    esp,0x8
  45d353:	85 c0                	test   eax,eax
  45d355:	74 30                	je     0x45d387
  45d357:	8d 85 5c ff ff ff    	lea    eax,[ebp-0xa4]
  45d35d:	50                   	push   eax
  45d35e:	8d 85 50 ff ff ff    	lea    eax,[ebp-0xb0]
  45d364:	50                   	push   eax
  45d365:	68 00 31 6b 00       	push   0x6b3100
  45d36a:	53                   	push   ebx
  45d36b:	e8 b0 49 08 00       	call   0x4e1d20
  45d370:	83 c4 10             	add    esp,0x10
  45d373:	85 c0                	test   eax,eax
  45d375:	75 42                	jne    0x45d3b9
  45d377:	ff 0b                	dec    DWORD PTR [ebx]
  45d379:	75 0c                	jne    0x45d387
  45d37b:	8b 43 04             	mov    eax,DWORD PTR [ebx+0x4]
  45d37e:	53                   	push   ebx
  45d37f:	8b 40 18             	mov    eax,DWORD PTR [eax+0x18]
  45d382:	ff d0                	call   eax
  45d384:	83 c4 04             	add    esp,0x4
  45d387:	33 f6                	xor    esi,esi
  45d389:	8d 8d 24 ff ff ff    	lea    ecx,[ebp-0xdc]
  45d38f:	c7 45 fc ff ff ff ff 	mov    DWORD PTR [ebp-0x4],0xffffffff
  45d396:	e8 15 c3 1a 00       	call   0x6096b0
  45d39b:	8b c6                	mov    eax,esi
  45d39d:	8b 4d f4             	mov    ecx,DWORD PTR [ebp-0xc]
  45d3a0:	64 89 0d 00 00 00 00 	mov    DWORD PTR fs:0x0,ecx
  45d3a7:	59                   	pop    ecx
  45d3a8:	5f                   	pop    edi
  45d3a9:	5e                   	pop    esi
  45d3aa:	5b                   	pop    ebx
  45d3ab:	8b 4d f0             	mov    ecx,DWORD PTR [ebp-0x10]
  45d3ae:	33 cd                	xor    ecx,ebp
  45d3b0:	e8 ef 3c 16 00       	call   0x5c10a4
  45d3b5:	8b e5                	mov    esp,ebp
  45d3b7:	5d                   	pop    ebp
  45d3b8:	c3                   	ret
  45d3b9:	8b 8d 6c ff ff ff    	mov    ecx,DWORD PTR [ebp-0x94]
  45d3bf:	8b 9d 5c ff ff ff    	mov    ebx,DWORD PTR [ebp-0xa4]
  45d3c5:	8b bd 50 ff ff ff    	mov    edi,DWORD PTR [ebp-0xb0]
  45d3cb:	89 9d 64 ff ff ff    	mov    DWORD PTR [ebp-0x9c],ebx
  45d3d1:	89 bd 60 ff ff ff    	mov    DWORD PTR [ebp-0xa0],edi
  45d3d7:	8d 51 01             	lea    edx,[ecx+0x1]
  45d3da:	c7 85 68 ff ff ff 00 	mov    DWORD PTR [ebp-0x98],0x0
  45d3e1:	00 00 00 
  45d3e4:	8a 01                	mov    al,BYTE PTR [ecx]
  45d3e6:	41                   	inc    ecx
  45d3e7:	84 c0                	test   al,al
  45d3e9:	75 f9                	jne    0x45d3e4
  45d3eb:	2b ca                	sub    ecx,edx
  45d3ed:	85 c9                	test   ecx,ecx
  45d3ef:	0f 8e 96 00 00 00    	jle    0x45d48b
  45d3f5:	8b 85 6c ff ff ff    	mov    eax,DWORD PTR [ebp-0x94]
  45d3fb:	be 02 00 00 00       	mov    esi,0x2
  45d400:	83 c0 fe             	add    eax,0xfffffffe
  45d403:	c7 85 68 ff ff ff 79 	mov    DWORD PTR [ebp-0x98],0x7879
  45d40a:	78 00 00 
  45d40d:	89 85 40 ff ff ff    	mov    DWORD PTR [ebp-0xc0],eax
  45d413:	33 db                	xor    ebx,ebx
  45d415:	0f b6 3c 30          	movzx  edi,BYTE PTR [eax+esi*1]
  45d419:	8d 4e 05             	lea    ecx,[esi+0x5]
  45d41c:	8d 46 fe             	lea    eax,[esi-0x2]
  45d41f:	83 f8 05             	cmp    eax,0x5
  45d422:	7d 0b                	jge    0x45d42f
  45d424:	8d 46 ff             	lea    eax,[esi-0x1]
  45d427:	0f af c8             	imul   ecx,eax
  45d42a:	0f af ce             	imul   ecx,esi
  45d42d:	eb 06                	jmp    0x45d435
  45d42f:	8d 46 01             	lea    eax,[esi+0x1]
  45d432:	0f af c8             	imul   ecx,eax
  45d435:	85 c9                	test   ecx,ecx
  45d437:	7e 1e                	jle    0x45d457
  45d439:	8d a4 24 00 00 00 00 	lea    esp,[esp+0x0]
  45d440:	69 c7 79 7e 00 00    	imul   eax,edi,0x7e79
  45d446:	05 9f 13 9a 02       	add    eax,0x29a139f
  45d44b:	99                   	cdq
  45d44c:	f7 bd 68 ff ff ff    	idiv   DWORD PTR [ebp-0x98]
  45d452:	33 fa                	xor    edi,edx
  45d454:	49                   	dec    ecx
  45d455:	75 e9                	jne    0x45d440
  45d457:	8b 8d 6c ff ff ff    	mov    ecx,DWORD PTR [ebp-0x94]
  45d45d:	33 df                	xor    ebx,edi
  45d45f:	46                   	inc    esi
  45d460:	8d 51 01             	lea    edx,[ecx+0x1]
  45d463:	8a 01                	mov    al,BYTE PTR [ecx]
  45d465:	41                   	inc    ecx
  45d466:	84 c0                	test   al,al
  45d468:	75 f9                	jne    0x45d463
  45d46a:	8d 46 fe             	lea    eax,[esi-0x2]
  45d46d:	2b ca                	sub    ecx,edx
  45d46f:	3b c1                	cmp    eax,ecx
  45d471:	8b 85 40 ff ff ff    	mov    eax,DWORD PTR [ebp-0xc0]
  45d477:	7c 9c                	jl     0x45d415
  45d479:	8b bd 60 ff ff ff    	mov    edi,DWORD PTR [ebp-0xa0]
  45d47f:	89 9d 68 ff ff ff    	mov    DWORD PTR [ebp-0x98],ebx
  45d485:	8b 9d 64 ff ff ff    	mov    ebx,DWORD PTR [ebp-0x9c]
  45d48b:	b8 67 66 66 66       	mov    eax,0x66666667
  45d490:	33 c9                	xor    ecx,ecx
  45d492:	f7 eb                	imul   ebx
  45d494:	33 f6                	xor    esi,esi
  45d496:	d1 fa                	sar    edx,1
  45d498:	8b c2                	mov    eax,edx
  45d49a:	c1 e8 1f             	shr    eax,0x1f
  45d49d:	03 c2                	add    eax,edx
  45d49f:	89 85 60 ff ff ff    	mov    DWORD PTR [ebp-0xa0],eax
  45d4a5:	85 db                	test   ebx,ebx
  45d4a7:	0f 8e 88 00 00 00    	jle    0x45d535
  45d4ad:	c7 85 64 ff ff ff 63 	mov    DWORD PTR [ebp-0x9c],0x7f63
  45d4b4:	7f 00 00 
  45d4b7:	eb 07                	jmp    0x45d4c0
  45d4b9:	8d a4 24 00 00 00 00 	lea    esp,[esp+0x0]
  45d4c0:	8b 85 68 ff ff ff    	mov    eax,DWORD PTR [ebp-0x98]
  45d4c6:	99                   	cdq
  45d4c7:	81 e2 ff 00 00 00    	and    edx,0xff
  45d4cd:	03 c2                	add    eax,edx
  45d4cf:	8b 95 68 ff ff ff    	mov    edx,DWORD PTR [ebp-0x98]
  45d4d5:	c1 f8 08             	sar    eax,0x8
  45d4d8:	03 85 60 ff ff ff    	add    eax,DWORD PTR [ebp-0xa0]
  45d4de:	03 f0                	add    esi,eax
  45d4e0:	81 e2 ff 00 00 80    	and    edx,0x800000ff
  45d4e6:	79 08                	jns    0x45d4f0
  45d4e8:	4a                   	dec    edx
  45d4e9:	81 ca 00 ff ff ff    	or     edx,0xffffff00
  45d4ef:	42                   	inc    edx
  45d4f0:	3b ce                	cmp    ecx,esi
  45d4f2:	7d 0f                	jge    0x45d503
  45d4f4:	3b cb                	cmp    ecx,ebx
  45d4f6:	7d 0b                	jge    0x45d503
  45d4f8:	30 14 39             	xor    BYTE PTR [ecx+edi*1],dl
  45d4fb:	8d 04 39             	lea    eax,[ecx+edi*1]
  45d4fe:	41                   	inc    ecx
  45d4ff:	3b ce                	cmp    ecx,esi
  45d501:	7c f1                	jl     0x45d4f4
  45d503:	8b 8d 68 ff ff ff    	mov    ecx,DWORD PTR [ebp-0x98]
  45d509:	69 c1 8b 78 00 00    	imul   eax,ecx,0x788b
  45d50f:	05 df 43 45 02       	add    eax,0x24543df
  45d514:	99                   	cdq
  45d515:	f7 bd 64 ff ff ff    	idiv   DWORD PTR [ebp-0x9c]
  45d51b:	33 ca                	xor    ecx,edx
  45d51d:	89 8d 68 ff ff ff    	mov    DWORD PTR [ebp-0x98],ecx
  45d523:	8b ce                	mov    ecx,esi
  45d525:	3b f3                	cmp    esi,ebx
  45d527:	7c 97                	jl     0x45d4c0
  45d529:	8b 9d 5c ff ff ff    	mov    ebx,DWORD PTR [ebp-0xa4]
  45d52f:	8b bd 50 ff ff ff    	mov    edi,DWORD PTR [ebp-0xb0]
  45d535:	53                   	push   ebx
  45d536:	57                   	push   edi
  45d537:	e8 84 7a 0a 00       	call   0x504fc0
  45d53c:	8b f8                	mov    edi,eax
  45d53e:	6a 00                	push   0x0
  45d540:	57                   	push   edi
  45d541:	ff b5 6c ff ff ff    	push   DWORD PTR [ebp-0x94]
  45d547:	e8 94 0a 09 00       	call   0x4edfe0
  45d54c:	83 c4 14             	add    esp,0x14
  45d54f:	8b f0                	mov    esi,eax
  45d551:	ff 0f                	dec    DWORD PTR [edi]
  45d553:	75 0c                	jne    0x45d561
  45d555:	8b 47 04             	mov    eax,DWORD PTR [edi+0x4]
  45d558:	57                   	push   edi
  45d559:	8b 40 18             	mov    eax,DWORD PTR [eax+0x18]
  45d55c:	ff d0                	call   eax
  45d55e:	83 c4 04             	add    esp,0x4
  45d561:	8b 8d 44 ff ff ff    	mov    ecx,DWORD PTR [ebp-0xbc]
  45d567:	ff 09                	dec    DWORD PTR [ecx]
  45d569:	0f 85 1a fe ff ff    	jne    0x45d389
  45d56f:	8b 41 04             	mov    eax,DWORD PTR [ecx+0x4]
  45d572:	51                   	push   ecx
  45d573:	8b 40 18             	mov    eax,DWORD PTR [eax+0x18]
  45d576:	ff d0                	call   eax
  45d578:	83 c4 04             	add    esp,0x4
  45d57b:	e9 09 fe ff ff       	jmp    0x45d389
