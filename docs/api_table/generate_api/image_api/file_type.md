# File Type

用于判定文件读取类型的结构

可以为以下三种结构
``` json
{
    "type": "path",
    "path": "path/to/file"
}
```

``` json
{
    "type": "url",
    "url": "https://example.com/path/to/file"
}
```

``` json
{
    "type": "base64",
    "base64": "base64 encoded string"
}
```