# ErisPulse-HelpModule
ErisPulse 帮助命令模块，提供自动化的命令帮助系统，支持查看所有可用命令及其用法说明

> **2.7.0+ 用户推荐使用 [ErisPulse-HelpNext](https://pypi.org/project/ErisPulse-HelpNext/)**（Takumi 图片渲染 / 昼夜主题 / 完整 i18n）。
> 本模块（HelpModule）继续保留，优先保持**向后兼容性**，适合无法使用 Takumi 图片渲染或停留在旧版本的环境。

## 功能特性
提供 Event 子模块中 command 模块中统一的命令帮助功能
- 自动收集并显示所有已注册的命令
- 支持通过序号查看特定命令的详细帮助信息
- 支持命令分组显示
- 可配置是否显示隐藏命令
- 支持命令别名显示

## 使用方法

### 基本命令

```
/help           # 显示所有可用命令的列表
/help <序号>     # 显示指定序号命令的详细帮助信息
```

### 命令别名

```
/h              # 等同于 /help
/帮助            # 等同于 /help
```

## 配置选项

模块支持以下配置选项，可以在 config.toml 中进行自定义：

```toml
[HelpModule]
show_hidden_commands = false  # 是否显示隐藏命令
group_commands = true         # 是否按组显示命令
```

### 配置说明

- `show_hidden_commands`: 设置为 `true` 时，帮助命令会显示被标记为隐藏的命令
- `group_commands`: 设置为 `false` 时，不按组显示命令，所有命令将在同一列表中显示

## 依赖

- ErisPulse SDK 2.2.0+

## 升级到 Next

如果你在使用 ErisPulse 2.7.0+ 且需要图片化帮助（Apple 风格卡片、昼夜主题、多语言），请安装 HelpNext：

```bash
epsdk install HelpNext
epsdk uninstall HelpModule
```

> 注意：HelpModule 与 HelpNext 都注册 `/help` 命令，请只启用其中一个。
