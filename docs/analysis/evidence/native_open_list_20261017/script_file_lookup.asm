
mxmain.dll:     file format pei-i386


Disassembly of section .text:

00609760 <.text+0x208760>:
  609760:	55                   	push   ebp
  609761:	8b ec                	mov    ebp,esp
  609763:	56                   	push   esi
  609764:	68 9c 70 79 00       	push   0x79709c
  609769:	ff 75 0c             	push   DWORD PTR [ebp+0xc]
  60976c:	8b f1                	mov    esi,ecx
  60976e:	ff 75 08             	push   DWORD PTR [ebp+0x8]
  609771:	e8 7a 00 00 00       	call   0x6097f0
  609776:	85 c0                	test   eax,eax
  609778:	75 07                	jne    0x609781
  60977a:	8b ce                	mov    ecx,esi
  60977c:	e8 0f 00 00 00       	call   0x609790
  609781:	5e                   	pop    esi
  609782:	5d                   	pop    ebp
  609783:	c2 08 00             	ret    0x8
  609786:	cc                   	int3
  609787:	cc                   	int3
  609788:	cc                   	int3
  609789:	cc                   	int3
  60978a:	cc                   	int3
  60978b:	cc                   	int3
  60978c:	cc                   	int3
  60978d:	cc                   	int3
  60978e:	cc                   	int3
  60978f:	cc                   	int3
  609790:	56                   	push   esi
  609791:	57                   	push   edi
  609792:	8b f9                	mov    edi,ecx
  609794:	8b 77 14             	mov    esi,DWORD PTR [edi+0x14]
  609797:	8d 46 01             	lea    eax,[esi+0x1]
  60979a:	50                   	push   eax
  60979b:	e8 e0 21 e4 ff       	call   0x44b980
  6097a0:	83 c4 04             	add    esp,0x4
  6097a3:	89 47 04             	mov    DWORD PTR [edi+0x4],eax
  6097a6:	8b cf                	mov    ecx,edi
  6097a8:	c6 04 30 00          	mov    BYTE PTR [eax+esi*1],0x0
  6097ac:	ff 77 14             	push   DWORD PTR [edi+0x14]
  6097af:	c7 47 10 00 00 00 00 	mov    DWORD PTR [edi+0x10],0x0
  6097b6:	ff 77 04             	push   DWORD PTR [edi+0x4]
  6097b9:	e8 c2 04 00 00       	call   0x609c80
  6097be:	8b 07                	mov    eax,DWORD PTR [edi]
  6097c0:	85 c0                	test   eax,eax
  6097c2:	74 0f                	je     0x6097d3
  6097c4:	50                   	push   eax
  6097c5:	e8 e9 8e fb ff       	call   0x5c26b3
  6097ca:	83 c4 04             	add    esp,0x4
  6097cd:	c7 07 00 00 00 00    	mov    DWORD PTR [edi],0x0
  6097d3:	c7 47 10 00 00 00 00 	mov    DWORD PTR [edi+0x10],0x0
  6097da:	33 c0                	xor    eax,eax
  6097dc:	c7 47 0c 00 00 00 00 	mov    DWORD PTR [edi+0xc],0x0
  6097e3:	5f                   	pop    edi
  6097e4:	5e                   	pop    esi
  6097e5:	c3                   	ret
  6097e6:	cc                   	int3
  6097e7:	cc                   	int3
  6097e8:	cc                   	int3
  6097e9:	cc                   	int3
  6097ea:	cc                   	int3
  6097eb:	cc                   	int3
  6097ec:	cc                   	int3
  6097ed:	cc                   	int3
  6097ee:	cc                   	int3
  6097ef:	cc                   	int3
  6097f0:	55                   	push   ebp
  6097f1:	8b ec                	mov    ebp,esp
  6097f3:	6a ff                	push   0xffffffff
  6097f5:	68 b3 b2 6a 00       	push   0x6ab2b3
  6097fa:	64 a1 00 00 00 00    	mov    eax,fs:0x0
  609800:	50                   	push   eax
  609801:	81 ec 40 02 00 00    	sub    esp,0x240
  609807:	a1 d0 13 82 00       	mov    eax,ds:0x8213d0
  60980c:	33 c5                	xor    eax,ebp
  60980e:	89 45 f0             	mov    DWORD PTR [ebp-0x10],eax
  609811:	53                   	push   ebx
  609812:	56                   	push   esi
  609813:	57                   	push   edi
  609814:	50                   	push   eax
  609815:	8d 45 f4             	lea    eax,[ebp-0xc]
  609818:	64 a3 00 00 00 00    	mov    fs:0x0,eax
  60981e:	8b f9                	mov    edi,ecx
  609820:	8b 45 10             	mov    eax,DWORD PTR [ebp+0x10]
  609823:	8b 75 0c             	mov    esi,DWORD PTR [ebp+0xc]
  609826:	8b 5d 08             	mov    ebx,DWORD PTR [ebp+0x8]
  609829:	89 85 bc fd ff ff    	mov    DWORD PTR [ebp-0x244],eax
  60982f:	33 c0                	xor    eax,eax
  609831:	89 85 b4 fd ff ff    	mov    DWORD PTR [ebp-0x24c],eax
  609837:	ff 77 04             	push   DWORD PTR [edi+0x4]
  60983a:	89 b5 b8 fd ff ff    	mov    DWORD PTR [ebp-0x248],esi
  609840:	89 85 c8 fd ff ff    	mov    DWORD PTR [ebp-0x238],eax
  609846:	e8 d5 21 e4 ff       	call   0x44ba20
  60984b:	8b 07                	mov    eax,DWORD PTR [edi]
  60984d:	83 c4 04             	add    esp,0x4
  609850:	c7 47 04 00 00 00 00 	mov    DWORD PTR [edi+0x4],0x0
  609857:	85 c0                	test   eax,eax
  609859:	74 0f                	je     0x60986a
  60985b:	50                   	push   eax
  60985c:	e8 52 8e fb ff       	call   0x5c26b3
  609861:	83 c4 04             	add    esp,0x4
  609864:	c7 07 00 00 00 00    	mov    DWORD PTR [edi],0x0
  60986a:	8d 47 0c             	lea    eax,[edi+0xc]
  60986d:	c7 47 10 00 00 00 00 	mov    DWORD PTR [edi+0x10],0x0
  609874:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  60987a:	89 85 b4 fd ff ff    	mov    DWORD PTR [ebp-0x24c],eax
  609880:	c7 00 00 00 00 00    	mov    DWORD PTR [eax],0x0
  609886:	e8 a5 b1 e4 ff       	call   0x454a30
  60988b:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [ebp-0x4],0x0
  609892:	85 f6                	test   esi,esi
  609894:	0f 84 8a 00 00 00    	je     0x609924
  60989a:	80 3e 00             	cmp    BYTE PTR [esi],0x0
  60989d:	c7 85 e8 fd ff ff 0f 	mov    DWORD PTR [ebp-0x218],0xf
  6098a4:	00 00 00 
  6098a7:	c7 85 e4 fd ff ff 00 	mov    DWORD PTR [ebp-0x21c],0x0
  6098ae:	00 00 00 
  6098b1:	c6 85 d4 fd ff ff 00 	mov    BYTE PTR [ebp-0x22c],0x0
  6098b8:	75 04                	jne    0x6098be
  6098ba:	33 c9                	xor    ecx,ecx
  6098bc:	eb 0e                	jmp    0x6098cc
  6098be:	8b ce                	mov    ecx,esi
  6098c0:	8d 51 01             	lea    edx,[ecx+0x1]
  6098c3:	8a 01                	mov    al,BYTE PTR [ecx]
  6098c5:	41                   	inc    ecx
  6098c6:	84 c0                	test   al,al
  6098c8:	75 f9                	jne    0x6098c3
  6098ca:	2b ca                	sub    ecx,edx
  6098cc:	51                   	push   ecx
  6098cd:	56                   	push   esi
  6098ce:	8d 8d d4 fd ff ff    	lea    ecx,[ebp-0x22c]
  6098d4:	e8 87 98 df ff       	call   0x403160
  6098d9:	83 bd e8 fd ff ff 10 	cmp    DWORD PTR [ebp-0x218],0x10
  6098e0:	8d 85 d4 fd ff ff    	lea    eax,[ebp-0x22c]
  6098e6:	6a 00                	push   0x0
  6098e8:	0f 43 85 d4 fd ff ff 	cmovae eax,DWORD PTR [ebp-0x22c]
  6098ef:	68 99 70 79 00       	push   0x797099
  6098f4:	50                   	push   eax
  6098f5:	c7 85 c8 fd ff ff 01 	mov    DWORD PTR [ebp-0x238],0x1
  6098fc:	00 00 00 
  6098ff:	e8 cc 7c e4 ff       	call   0x4515d0
  609904:	83 c4 0c             	add    esp,0xc
  609907:	85 c0                	test   eax,eax
  609909:	75 0b                	jne    0x609916
  60990b:	39 85 e4 fd ff ff    	cmp    DWORD PTR [ebp-0x21c],eax
  609911:	0f 95 c0             	setne  al
  609914:	85 c0                	test   eax,eax
  609916:	0f 94 c0             	sete   al
  609919:	c6 85 d3 fd ff ff 00 	mov    BYTE PTR [ebp-0x22d],0x0
  609920:	84 c0                	test   al,al
  609922:	74 07                	je     0x60992b
  609924:	c6 85 d3 fd ff ff 01 	mov    BYTE PTR [ebp-0x22d],0x1
  60992b:	f6 85 c8 fd ff ff 01 	test   BYTE PTR [ebp-0x238],0x1
  609932:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [ebp-0x4],0x0
  609939:	74 17                	je     0x609952
  60993b:	83 bd e8 fd ff ff 10 	cmp    DWORD PTR [ebp-0x218],0x10
  609942:	72 0e                	jb     0x609952
  609944:	ff b5 d4 fd ff ff    	push   DWORD PTR [ebp-0x22c]
  60994a:	e8 d1 20 e4 ff       	call   0x44ba20
  60994f:	83 c4 04             	add    esp,0x4
  609952:	80 bd d3 fd ff ff 00 	cmp    BYTE PTR [ebp-0x22d],0x0
  609959:	74 07                	je     0x609962
  60995b:	8b c3                	mov    eax,ebx
  60995d:	e9 bb 00 00 00       	jmp    0x609a1d
  609962:	56                   	push   esi
  609963:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  609969:	e8 22 b4 e4 ff       	call   0x454d90
  60996e:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  609974:	e8 67 b5 e4 ff       	call   0x454ee0
  609979:	85 c0                	test   eax,eax
  60997b:	0f 84 5f 02 00 00    	je     0x609be0
  609981:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  609987:	e8 44 b5 e4 ff       	call   0x454ed0
  60998c:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  609992:	8d 70 ff             	lea    esi,[eax-0x1]
  609995:	e8 46 b5 e4 ff       	call   0x454ee0
  60999a:	80 3c 30 2f          	cmp    BYTE PTR [eax+esi*1],0x2f
  60999e:	74 41                	je     0x6099e1
  6099a0:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  6099a6:	e8 25 b5 e4 ff       	call   0x454ed0
  6099ab:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  6099b1:	8d 70 ff             	lea    esi,[eax-0x1]
  6099b4:	e8 27 b5 e4 ff       	call   0x454ee0
  6099b9:	80 3c 30 5c          	cmp    BYTE PTR [eax+esi*1],0x5c
  6099bd:	74 22                	je     0x6099e1
  6099bf:	68 a8 70 79 00       	push   0x7970a8
  6099c4:	8d 8d c4 fd ff ff    	lea    ecx,[ebp-0x23c]
  6099ca:	e8 41 a6 e7 ff       	call   0x484010
  6099cf:	8d 85 c4 fd ff ff    	lea    eax,[ebp-0x23c]
  6099d5:	50                   	push   eax
  6099d6:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  6099dc:	e8 cf b8 e4 ff       	call   0x4552b0
  6099e1:	33 c0                	xor    eax,eax
  6099e3:	89 9d c4 fd ff ff    	mov    DWORD PTR [ebp-0x23c],ebx
  6099e9:	89 85 c8 fd ff ff    	mov    DWORD PTR [ebp-0x238],eax
  6099ef:	38 03                	cmp    BYTE PTR [ebx],al
  6099f1:	74 0d                	je     0x609a00
  6099f3:	40                   	inc    eax
  6099f4:	89 85 c8 fd ff ff    	mov    DWORD PTR [ebp-0x238],eax
  6099fa:	80 3c 18 00          	cmp    BYTE PTR [eax+ebx*1],0x0
  6099fe:	75 f3                	jne    0x6099f3
  609a00:	8d 85 c4 fd ff ff    	lea    eax,[ebp-0x23c]
  609a06:	50                   	push   eax
  609a07:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  609a0d:	e8 9e b8 e4 ff       	call   0x4552b0
  609a12:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  609a18:	e8 b3 b4 e4 ff       	call   0x454ed0
  609a1d:	ff b5 bc fd ff ff    	push   DWORD PTR [ebp-0x244]
  609a23:	50                   	push   eax
  609a24:	e8 b5 8f fb ff       	call   0x5c29de
  609a29:	8b f0                	mov    esi,eax
  609a2b:	83 c4 08             	add    esp,0x8
  609a2e:	85 f6                	test   esi,esi
  609a30:	74 37                	je     0x609a69
  609a32:	6a 02                	push   0x2
  609a34:	6a 00                	push   0x0
  609a36:	56                   	push   esi
  609a37:	89 37                	mov    DWORD PTR [edi],esi
  609a39:	c7 47 0c 00 00 00 00 	mov    DWORD PTR [edi+0xc],0x0
  609a40:	e8 d4 0c fc ff       	call   0x5ca719
  609a45:	56                   	push   esi
  609a46:	e8 e1 10 fc ff       	call   0x5cab2c
  609a4b:	6a 00                	push   0x0
  609a4d:	6a 00                	push   0x0
  609a4f:	56                   	push   esi
  609a50:	89 47 14             	mov    DWORD PTR [edi+0x14],eax
  609a53:	e8 c1 0c fc ff       	call   0x5ca719
  609a58:	83 c4 1c             	add    esp,0x1c
  609a5b:	c7 47 10 00 00 00 00 	mov    DWORD PTR [edi+0x10],0x0
  609a62:	33 f6                	xor    esi,esi
  609a64:	e9 7c 01 00 00       	jmp    0x609be5
  609a69:	8b 85 b8 fd ff ff    	mov    eax,DWORD PTR [ebp-0x248]
  609a6f:	85 c0                	test   eax,eax
  609a71:	0f 84 69 01 00 00    	je     0x609be0
  609a77:	53                   	push   ebx
  609a78:	50                   	push   eax
  609a79:	e8 c2 06 00 00       	call   0x60a140
  609a7e:	8b c8                	mov    ecx,eax
  609a80:	83 c4 08             	add    esp,0x8
  609a83:	85 c9                	test   ecx,ecx
  609a85:	75 08                	jne    0x609a8f
  609a87:	8d 70 02             	lea    esi,[eax+0x2]
  609a8a:	e9 56 01 00 00       	jmp    0x609be5
  609a8f:	8d 47 18             	lea    eax,[edi+0x18]
  609a92:	50                   	push   eax
  609a93:	8d 57 14             	lea    edx,[edi+0x14]
  609a96:	52                   	push   edx
  609a97:	8d 47 0c             	lea    eax,[edi+0xc]
  609a9a:	89 95 bc fd ff ff    	mov    DWORD PTR [ebp-0x244],edx
  609aa0:	50                   	push   eax
  609aa1:	53                   	push   ebx
  609aa2:	e8 59 42 00 00       	call   0x60dd00
  609aa7:	8b f0                	mov    esi,eax
  609aa9:	85 f6                	test   esi,esi
  609aab:	75 08                	jne    0x609ab5
  609aad:	8d 70 03             	lea    esi,[eax+0x3]
  609ab0:	e9 30 01 00 00       	jmp    0x609be5
  609ab5:	b9 64 d1 93 00       	mov    ecx,0x93d164
  609aba:	c7 47 10 ff ff ff ff 	mov    DWORD PTR [edi+0x10],0xffffffff
  609ac1:	e8 0a b4 e4 ff       	call   0x454ed0
  609ac6:	50                   	push   eax
  609ac7:	8d 8d c0 fd ff ff    	lea    ecx,[ebp-0x240]
  609acd:	e8 6e af e4 ff       	call   0x454a40
  609ad2:	56                   	push   esi
  609ad3:	8d 8d b8 fd ff ff    	lea    ecx,[ebp-0x248]
  609ad9:	c6 45 fc 02          	mov    BYTE PTR [ebp-0x4],0x2
  609add:	e8 5e af e4 ff       	call   0x454a40
  609ae2:	8b f0                	mov    esi,eax
  609ae4:	8b ce                	mov    ecx,esi
  609ae6:	c6 45 fc 03          	mov    BYTE PTR [ebp-0x4],0x3
  609aea:	e8 e1 b3 e4 ff       	call   0x454ed0
  609aef:	8b ce                	mov    ecx,esi
  609af1:	89 85 c4 fd ff ff    	mov    DWORD PTR [ebp-0x23c],eax
  609af7:	e8 e4 b3 e4 ff       	call   0x454ee0
  609afc:	89 85 c8 fd ff ff    	mov    DWORD PTR [ebp-0x238],eax
  609b02:	8d 8d c0 fd ff ff    	lea    ecx,[ebp-0x240]
  609b08:	8d 85 c4 fd ff ff    	lea    eax,[ebp-0x23c]
  609b0e:	50                   	push   eax
  609b0f:	e8 9c b7 e4 ff       	call   0x4552b0
  609b14:	8d 8d b8 fd ff ff    	lea    ecx,[ebp-0x248]
  609b1a:	c6 45 fc 02          	mov    BYTE PTR [ebp-0x4],0x2
  609b1e:	e8 bd ae e4 ff       	call   0x4549e0
  609b23:	8d 8d c0 fd ff ff    	lea    ecx,[ebp-0x240]
  609b29:	e8 a2 b3 e4 ff       	call   0x454ed0
  609b2e:	68 ac 70 79 00       	push   0x7970ac
  609b33:	50                   	push   eax
  609b34:	e8 a5 8e fb ff       	call   0x5c29de
  609b39:	83 c4 08             	add    esp,0x8
  609b3c:	89 07                	mov    DWORD PTR [edi],eax
  609b3e:	85 c0                	test   eax,eax
  609b40:	0f 85 7e 00 00 00    	jne    0x609bc4
  609b46:	8d 85 ec fe ff ff    	lea    eax,[ebp-0x114]
  609b4c:	50                   	push   eax
  609b4d:	68 04 01 00 00       	push   0x104
  609b52:	ff 15 80 03 6b 00    	call   DWORD PTR ds:0x6b0380
  609b58:	8d 8d c0 fd ff ff    	lea    ecx,[ebp-0x240]
  609b5e:	e8 6d b3 e4 ff       	call   0x454ed0
  609b63:	8b f0                	mov    esi,eax
  609b65:	e8 32 9e fb ff       	call   0x5c399c
  609b6a:	8d 8d ec fe ff ff    	lea    ecx,[ebp-0x114]
  609b70:	51                   	push   ecx
  609b71:	ff 30                	push   DWORD PTR [eax]
  609b73:	e8 c3 9f fb ff       	call   0x5c3b3b
  609b78:	83 c4 04             	add    esp,0x4
  609b7b:	50                   	push   eax
  609b7c:	56                   	push   esi
  609b7d:	68 b0 70 79 00       	push   0x7970b0
  609b82:	8d 85 ec fd ff ff    	lea    eax,[ebp-0x214]
  609b88:	68 00 01 00 00       	push   0x100
  609b8d:	50                   	push   eax
  609b8e:	e8 c5 ac fb ff       	call   0x5c4858
  609b93:	8b 85 b4 fd ff ff    	mov    eax,DWORD PTR [ebp-0x24c]
  609b99:	8d 8d c0 fd ff ff    	lea    ecx,[ebp-0x240]
  609b9f:	83 c4 18             	add    esp,0x18
  609ba2:	c6 45 fc 00          	mov    BYTE PTR [ebp-0x4],0x0
  609ba6:	be 01 00 00 00       	mov    esi,0x1
  609bab:	c7 00 00 00 00 00    	mov    DWORD PTR [eax],0x0
  609bb1:	8b 85 bc fd ff ff    	mov    eax,DWORD PTR [ebp-0x244]
  609bb7:	c7 00 00 00 00 00    	mov    DWORD PTR [eax],0x0
  609bbd:	e8 1e ae e4 ff       	call   0x4549e0
  609bc2:	eb 21                	jmp    0x609be5
  609bc4:	6a 00                	push   0x0
  609bc6:	8b cf                	mov    ecx,edi
  609bc8:	e8 53 00 00 00       	call   0x609c20
  609bcd:	8d 8d c0 fd ff ff    	lea    ecx,[ebp-0x240]
  609bd3:	c6 45 fc 00          	mov    BYTE PTR [ebp-0x4],0x0
  609bd7:	33 f6                	xor    esi,esi
  609bd9:	e8 02 ae e4 ff       	call   0x4549e0
  609bde:	eb 05                	jmp    0x609be5
  609be0:	be 01 00 00 00       	mov    esi,0x1
  609be5:	8d 8d cc fd ff ff    	lea    ecx,[ebp-0x234]
  609beb:	c7 45 fc ff ff ff ff 	mov    DWORD PTR [ebp-0x4],0xffffffff
  609bf2:	e8 e9 ad e4 ff       	call   0x4549e0
  609bf7:	8b c6                	mov    eax,esi
  609bf9:	8b 4d f4             	mov    ecx,DWORD PTR [ebp-0xc]
  609bfc:	64 89 0d 00 00 00 00 	mov    DWORD PTR fs:0x0,ecx
  609c03:	59                   	pop    ecx
  609c04:	5f                   	pop    edi
  609c05:	5e                   	pop    esi
  609c06:	5b                   	pop    ebx
  609c07:	8b 4d f0             	mov    ecx,DWORD PTR [ebp-0x10]
  609c0a:	33 cd                	xor    ecx,ebp
  609c0c:	e8 93 74 fb ff       	call   0x5c10a4
  609c11:	8b e5                	mov    esp,ebp
  609c13:	5d                   	pop    ebp
  609c14:	c2                   	.byte 0xc2
