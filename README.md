# find_large_file
调用 ncdu 来定位文件系统中占用了较大空间的文件、目录，使用前请先安装 ncdu，参考： https://dev.yorhel.nl/ncdu

### 参数说明：
`--larger-than`或`-M` ：指定找出大于多少 MB 的文件，默认值为 100MB

`--top`或`-T` : 指定列出最大的多少个文件，默认值为 20 个

`--exclude` ：指定排除含有哪些字符串的文件

`--exclude-caches` : 同 ncdu 命令的 --exclude-caches，排除 Cache 目录

### 举例：

```bash
./finder.py -T10 --exclude=pdf ~/Documents  # 找到 ~/Documents 目录下不含有 “pdf” 的最大的10个文件
```