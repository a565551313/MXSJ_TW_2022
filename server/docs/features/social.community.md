# 空间、相册、动态与互动

工作包：`social.community`；当前归口：`social`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

上传安全、隐私、内容审核属于独立工程要求。

## 接口设计起点

`publish_post / list_feed / react_to_post / report_content`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 25 | `script/mxgame/myqnew/model/mdmyqmsglist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 33 | `script/mxgame/myqnew/view/dlgmyqsingleshow.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 72 | `script/mxgame/myqnew/logicaddshowmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 116 | `script/mxgame/myq/dlgmyq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SRefresh, C2SRefresh |
| 125 | `script/mxgame/myqnew/view/dlgmyqmsgitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 165 | `script/mxgame/myq/myqbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 250 | `script/mxgame/myqnew/logicphotomgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 254 | `script/mxgame/myqnew/dgt/dgtmyqfriendmainsmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 265 | `script/mxgame/myqnew/myqtest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 278 | `script/mxgame/myqnew/model/mdmyqfriendlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 368 | `script/mxgame/myqnew/view/dlgmyqshareshot.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 398 | `script/mxgame/myqnew/view/dlgmyqaitefriendlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 403 | `script/mxgame/myqnew/view/dlgmyqreply.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 410 | `script/mxgame/album/dlgalbumcharsourcereview1.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 414 | `script/mxgame/myqnew/view/myqitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 428 | `script/mxgame/myqnew/view/dlgmyqdelete.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 440 | `script/mxgame/album/dlgalbumscreenshot.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 533 | `script/mxgame/myqnew/dgt/dgtnewmyqmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 554 | `script/mxgame/album/dlgalbumcharsource.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 575 | `script/mxgame/myqnew/newmyqbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 766 | `script/mxgame/myqnew/view/dlgmyqissuenew.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 787 | `script/mxgame/myqnew/view/dlgmyqmsgitem_mini.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 888 | `script/mxgame/myqnew/dgt/dgtmyqfriendred.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 937 | `script/mxgame/myqnew/test_myqlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 954 | `script/mxgame/myqnew/model/mdmyqextinfo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 978 | `script/netblog.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CArticalData, S2CShowRegedit, S2CIsShowRegeditBtn, S2CBlog, C2SGetF19, C2SGetF19A |
| 1022 | `script/mxgame/myqnew/view/dlgmyqsharegoods.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1148 | `script/mxgame/myqnew/dgt/dgtmyqmsglist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1210 | `script/mxgame/album/dlgalbumcharsourcereview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1320 | `script/mxgame/myqnew/view/dlgmyqfriendmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1474 | `script/mxgame/myq/myqdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CProcess |
| 1507 | `script/mxgame/myq/netmyq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SGetToken, C2SGetSharUrl, C2SOpenFirendMYQ, C2SIssueNewSuccess, S2CMengYouQuan, S2CGetToken |
| 1530 | `script/mxgame/album/dlgalbumbgsourcereview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1623 | `script/mxgame/album/dlgalbumgraffity.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1681 | `script/mxgame/myqnew/view/dlgmyqfilter.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1701 | `script/mxgame/album/dlgalbumpicsourcereview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1831 | `script/mxgame/myqnew/model/mdmyq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CProcess |
| 1871 | `script/mxgame/myqnew/view/dlgnewmyqmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1932 | `script/mxgame/album/dlgalbumpicsourcereview1.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1937 | `script/mxgame/myqnew/logicrefreshuserinfo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2025 | `script/mxgame/album/dlgalbumbgsource.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2032 | `script/mxgame/album/dlgalbummainpage.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2106 | `script/mxgame/myqnew/view/dlgmyqnewphoto.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2133 | `script/mxgame/myqnew/view/dlgmyqfriendmainsmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2172 | `script/mxgame/album/dlgalbumsetname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2188 | `script/mxgame/myqnew/view/dlgmyqdongtai.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2228 | `script/mxgame/myqnew/dgt/dgtmyqsingleshow.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2274 | `script/mxgame/album/albumpublic.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2440 | `script/mxgame/myqnew/dgt/dgtmyqdongtai.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2546 | `script/mxgame/myqnew/myqinterface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2555 | `script/mxgame/myqnew/view/dlgmyqlocation.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2636 | `script/mxgame/myqnew/dgt/dgtmyqnewphoto.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2707 | `script/mxgame/myqnew/view/dlgmyqshareimage.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2729 | `script/mxgame/album/dlgalbumtext.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2825 | `script/mxgame/myqnew/view/dlgmyqdongtaismall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2835 | `script/mxgame/album/dlgalbumsend.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2868 | `script/mxgame/myqnew/dgt/dgtmyqfriendlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2927 | `script/mxgame/myqnew/view/myqphotoitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3223 | `script/mxgame/myqnew/view/dlgmyqreport.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3247 | `script/mxgame/myqnew/view/dlgmyqmsglist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3342 | `script/mxgame/myqnew/view/dlgmyqmsglist_mini.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3506 | `script/mxgame/myq/myqmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CProcess, S2CAddTalks, S2CAddTalk, S2CDelTalk, S2CTalkComments, S2CAddTalkComment |
| 3516 | `script/mxgame/myq/dlgmyqphoto.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3762 | `script/mxgame/myqnew/myqsignal.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3867 | `script/mxgame/myqnew/myqdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4188 | `script/mxgame/myqnew/dgt/dgtmyqfriendmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4250 | `script/mxgame/album/netalbum.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CLock, S2CUnLock, S2CLockCheck, S2CUploadAlbum, S2CSendAlbum, S2CDelAlbum |
| 4262 | `script/mxgame/myqnew/netnewmyq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSRequestFrdZonePage, C2GSAddShow, C2GSDelShow, C2GSComment, C2GSDelComment, C2GSPro |
| 4322 | `script/mxgame/myqnew/model/mdmyqnewphoto.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4325 | `script/mxgame/myqnew/view/dlgmyqbigmsglist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4535 | `script/mxgame/album/dlgnewalbum.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4587 | `script/mxgame/album/dlgalbumreview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4830 | `script/mxgame/myqnew/myqcontext.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CAddTalks, S2CAddTalk, S2CTalkPraise, S2CTalkPraises, S2CDelTalk, S2CTalkCommentChange |
| 4847 | `script/mxgame/myqnew/view/dlgmyqmsglistsmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
