"""
帮助模块模板系统
提供多平台支持的消息模板
"""

from typing import Dict, List, Optional

from ErisPulse.Core.Event import command


class HelpTemplates:
    """帮助模块模板类"""

    # 配色方案
    PRIMARY_COLOR = "#1565c0"  # 蓝色 - 主标题
    SUCCESS_COLOR = "#2e7d32"  # 绿色 - 成功信息
    WARNING_COLOR = "#e65100"  # 橙色 - 警告信息
    ERROR_COLOR = "#b71c1c"  # 红色 - 错误信息

    # 半透明背景色
    PRIMARY_BG = "rgba(21, 101, 192, 0.05)"
    SUCCESS_BG = "rgba(76, 175, 80, 0.1)"
    WARNING_BG = "rgba(255, 167, 38, 0.15)"
    ERROR_BG = "rgba(183, 28, 28, 0.1)"

    @classmethod
    def _get_group_name(cls, group: str) -> str:
        if group == "default":
            return "通用命令"
        return f"{group}命令" if group else "其他"

    @classmethod
    def _other_prefixes(cls, prefixes: list, display_prefix: str) -> list:
        """获取除主前缀外的其他前缀"""
        if not prefixes or len(prefixes) <= 1:
            return []
        return [p for p in prefixes if p != display_prefix]

    @classmethod
    def _prefix_note_html(cls, other_prefixes: list) -> str:
        if not other_prefixes:
            return ""
        note = "、".join(
            f"<code style='font-size:11px;'>{p}</code>" for p in other_prefixes
        )
        return f'<div style="font-size: 11px; color: #999; margin-top: 4px;">其他触发前缀: {note}</div>'

    @classmethod
    def _prefix_note_text(cls, other_prefixes: list) -> str:
        if not other_prefixes:
            return ""
        note = "、".join(other_prefixes)
        return f"\n其他触发前缀: {note}"

    # ==================== 帮助列表模板 ====================

    @classmethod
    def build_help_list(
        cls,
        commands: List[Dict],
        command_map: Dict[int, Dict],
        prefix: str,
        group_commands: bool = True,
        prefixes: Optional[list] = None,
    ) -> Dict[str, str]:
        other_prefixes = cls._other_prefixes(prefixes or [prefix], prefix)

        # 构建 HTML
        html = cls._build_help_list_html(
            commands, command_map, prefix, group_commands, other_prefixes
        )

        # 构建 Markdown
        markdown = cls._build_help_list_markdown(
            commands, command_map, prefix, group_commands, other_prefixes
        )

        # 构建 Text
        text = cls._build_help_list_text(
            commands, command_map, prefix, group_commands, other_prefixes
        )

        return {"html": html, "markdown": markdown, "text": text}

    @classmethod
    def _build_help_list_html(
        cls,
        commands: List[Dict],
        command_map: Dict[int, Dict],
        prefix: str,
        group_commands: bool,
        other_prefixes: Optional[list] = None,
    ) -> str:
        # 重置命令映射
        grouped = {}
        if group_commands:
            for cmd in commands:
                group = cmd["info"].get("group") or "default"
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(cmd)
        else:
            grouped["default"] = commands

        # 构建命令列表 HTML（带展开/折叠功能）
        commands_html = ""
        global_idx = 1

        for group, cmds in grouped.items():
            group_name = cls._get_group_name(group)

            commands_html += f"""
<div style="font-size:13px; margin-bottom: 8px; font-weight: bold; color: {cls.PRIMARY_COLOR};">{group_name}</div>
"""

            for cmd in cmds:
                name = cmd["name"]
                info = cmd["info"]
                help_text = info.get("help", "暂无描述")
                command_map[global_idx] = cmd

                # 构建命令详情内容
                detail_content = cls._build_command_detail_inline(name, info, prefix)

                commands_html += f"""<details style="margin-bottom: 8px;">
    <summary style="cursor: pointer; font-size: 13px; padding: 4px; background: rgba(0, 0, 0, 0.02); border-radius: 4px; display: flex; align-items: center;">
        <span style="font-weight: bold; margin-right: 8px;">{global_idx}.</span>
        <code style="background: rgba(0, 0, 0, 0.05); padding: 2px 6px; border-radius: 3px; margin-right: 8px;">{prefix}{name}</code>
        <span style="color: #666;">- {help_text}</span>
    </summary>
    <div style="padding: 8px; margin-top: 6px; border-left: 3px solid {cls.PRIMARY_BG}; background: rgba(0, 0, 0, 0.01); border-radius: 4px;">
        {detail_content}
    </div>
</details>"""
                global_idx += 1

            commands_html += "\n"

        # 构建完整 HTML
        html = f"""<div style="padding: 12px; border-radius: 8px;">
    <div style="color: {cls.PRIMARY_COLOR}; font-size: 16px; font-weight: bold; margin-bottom: 12px;">
        命令帮助
    </div>

    <div style="padding: 8px; background: {cls.PRIMARY_BG}; border-radius: 6px; margin-bottom: 12px;">
        <div style="font-size: 13px;">
            使用 '{prefix}help <序号>' 查看命令详情
        </div>
    </div>

    {commands_html}

    <div style="font-size: 12px; color: #666; margin-top: 8px;">
        共 {len(commands)} 个可用命令
    </div>
    {cls._prefix_note_html(other_prefixes or [])}
</div>"""

        return html

    @classmethod
    def _build_help_list_markdown(
        cls,
        commands: List[Dict],
        command_map: Dict[int, Dict],
        prefix: str,
        group_commands: bool,
        other_prefixes: Optional[list] = None,
    ) -> str:
        lines = ["**命令帮助**", "", f"使用 `{prefix}help <序号>` 查看命令详情", ""]

        global_idx = 1

        if group_commands:
            grouped = {}
            for cmd in commands:
                group = cmd["info"].get("group") or "default"
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(cmd)

            for group, cmds in grouped.items():
                group_name = cls._get_group_name(group)
                lines.append(f"**{group_name}**")
                lines.append("")

                for cmd in cmds:
                    name = cmd["name"]
                    help_text = cmd["info"].get("help", "暂无描述")
                    command_map[global_idx] = cmd
                    lines.append(f"{global_idx}. `{prefix}{name}` - {help_text}")
                    global_idx += 1

                lines.append("")
        else:
            lines.append("**所有命令**")
            lines.append("")
            for cmd in commands:
                name = cmd["name"]
                help_text = cmd["info"].get("help", "暂无描述")
                command_map[global_idx] = cmd
                lines.append(f"{global_idx}. `{prefix}{name}` - {help_text}")
                global_idx += 1
            lines.append("")

        lines.append("---")
        lines.append(f"共 {len(commands)} 个可用命令")
        if other_prefixes:
            lines.append("")
            lines.append(f"其他触发前缀: {'、'.join(other_prefixes)}")

        return "\n".join(lines)

    @classmethod
    def _build_help_list_text(
        cls,
        commands: List[Dict],
        command_map: Dict[int, Dict],
        prefix: str,
        group_commands: bool,
        other_prefixes: Optional[list] = None,
    ) -> str:
        lines = [
            "命令帮助",
            "----------",
            f"使用 '{prefix}help <序号>' 查看命令详情",
            "",
        ]

        global_idx = 1

        if group_commands:
            grouped = {}
            for cmd in commands:
                group = cmd["info"].get("group") or "default"
                if group not in grouped:
                    grouped[group] = []
                grouped[group].append(cmd)

            for group, cmds in grouped.items():
                group_name = cls._get_group_name(group)
                lines.append(f"[{group_name}]")
                lines.append("")

                for cmd in cmds:
                    name = cmd["name"]
                    help_text = cmd["info"].get("help", "暂无描述")
                    command_map[global_idx] = cmd
                    lines.append(f"{global_idx}. {prefix}{name} - {help_text}")
                    global_idx += 1

                lines.append("")
        else:
            lines.append("[所有命令]")
            lines.append("")
            for cmd in commands:
                name = cmd["name"]
                help_text = cmd["info"].get("help", "暂无描述")
                command_map[global_idx] = cmd
                lines.append(f"{global_idx}. {prefix}{name} - {help_text}")
                global_idx += 1
            lines.append("")

        lines.append("----------")
        lines.append(f"共 {len(commands)} 个可用命令")
        if other_prefixes:
            lines.append("")
            lines.append(f"其他触发前缀: {'、'.join(other_prefixes)}")

        return "\n".join(lines)

    @classmethod
    def _build_command_detail_inline(cls, name: str, info: Dict, prefix: str) -> str:
        """
        构建内联命令详情（用于展开区域）
        """
        parts = []

        # 描述
        parts.append(f"""<div style="margin-bottom: 8px;">
        <strong style="font-size: 12px; color: {cls.PRIMARY_COLOR};">描述:</strong>
        <span style="font-size: 12px; margin-left: 8px;">{info.get("help", "暂无描述")}</span>
    </div>""")

        # 别名 - 从全局 command.aliases 获取
        main_name = info.get("main_name", name)
        aliases = []
        for alias, mapped_name in command.aliases.items():
            if mapped_name == main_name and alias != main_name:
                aliases.append(alias)

        if aliases:
            aliases_text = ", ".join(
                f"<code style='font-size: 11px;'>{prefix}{a}</code>" for a in aliases
            )
            parts.append(f"""<div style="margin-bottom: 8px;">
        <strong style="font-size: 12px; color: {cls.PRIMARY_COLOR};">别名:</strong>
        <span style="font-size: 12px; margin-left: 8px;">{aliases_text}</span>
    </div>""")

        # 用法
        if info.get("usage"):
            parts.append(f"""<div style="margin-bottom: 8px;">
        <strong style="font-size: 12px; color: {cls.PRIMARY_COLOR};">用法:</strong>
        <span style="font-size: 12px; margin-left: 8px; font-family: monospace; background: rgba(0, 0, 0, 0.03); padding: 2px 6px; border-radius: 3px;">{info["usage"].replace("/", prefix)}</span>
    </div>""")

        # 权限
        if info.get("permission"):
            parts.append(f"""<div style="margin-bottom: 8px;">
        <strong style="font-size: 12px; color: {cls.PRIMARY_COLOR};">权限:</strong>
        <span style="font-size: 12px; margin-left: 8px; color: {cls.WARNING_COLOR};">需要特殊权限</span>
    </div>""")

        # 分组
        if info.get("group"):
            group_name = cls._get_group_name(info["group"])
            parts.append(f"""<div style="margin-bottom: 8px;">
        <strong style="font-size: 12px; color: {cls.PRIMARY_COLOR};">分组:</strong>
        <span style="font-size: 12px; margin-left: 8px;">{group_name}</span>
    </div>""")

        return "\n".join(parts)

    # ==================== 命令详情模板 ====================

    @classmethod
    def build_command_detail(
        cls, cmd: Dict, prefix: str, prefixes: Optional[list] = None
    ) -> Dict[str, str]:
        other_prefixes = cls._other_prefixes(prefixes or [prefix], prefix)

        # 构建 HTML
        html = cls._build_command_detail_html(cmd, prefix, other_prefixes)

        # 构建 Markdown
        markdown = cls._build_command_detail_markdown(cmd, prefix, other_prefixes)

        # 构建 Text
        text = cls._build_command_detail_text(cmd, prefix, other_prefixes)

        return {"html": html, "markdown": markdown, "text": text}

    @classmethod
    def _build_command_detail_html(
        cls, cmd: Dict, prefix: str, other_prefixes: Optional[list] = None
    ) -> str:
        name = cmd["name"]
        info = cmd["info"]

        html_parts = [
            f"""<div style="padding: 12px; border-radius: 8px;">
    <div style="color: {cls.PRIMARY_COLOR}; font-size: 16px; font-weight: bold; margin-bottom: 12px;">
        命令详情: {prefix}{name}
    </div>"""
        ]

        # 描述
        html_parts.append(f"""
    <div style="margin-bottom: 12px; border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px;">
        <div style="margin-bottom: 8px;">
            <strong style="font-size: 14px;">描述:</strong>
        </div>
        <div style="font-size: 13px;">
            {info.get("help", "暂无描述")}
        </div>
    </div>""")

        # 别名 - 从全局 command.aliases 获取
        main_name = info.get("main_name", name)
        aliases = []
        for alias, mapped_name in command.aliases.items():
            if mapped_name == main_name and alias != main_name:
                aliases.append(alias)

        if aliases:
            aliases_text = ", ".join(f"{prefix}{a}" for a in aliases)
            html_parts.append(f"""
    <div style="margin-bottom: 8px;">
        <div style="font-size: 13px; margin-bottom: 4px;">
            <strong>别名:</strong>
        </div>
        <div style="font-size: 13px;">
            {aliases_text}
        </div>
    </div>""")

        # 用法
        if info.get("usage"):
            html_parts.append(f"""
    <div style="margin-bottom: 8px;">
        <div style="font-size: 13px; margin-bottom: 4px;">
            <strong>用法:</strong>
        </div>
        <div style="font-size: 13px; font-family: monospace; background: rgba(0, 0, 0, 0.03); padding: 6px; border-radius: 4px;">
            {info["usage"].replace("/", prefix)}
        </div>
    </div>""")

        # 权限
        if info.get("permission"):
            html_parts.append(f"""
    <div style="margin-bottom: 8px;">
        <div style="font-size: 13px; margin-bottom: 4px;">
            <strong>权限:</strong>
        </div>
        <div style="font-size: 13px; color: {cls.WARNING_COLOR};">
            需要特殊权限
        </div>
    </div>""")

        # 分组
        if info.get("group"):
            group_name = cls._get_group_name(info["group"])
            html_parts.append(f"""
    <div style="margin-bottom: 8px;">
        <div style="font-size: 13px; margin-bottom: 4px;">
            <strong>分组:</strong>
        </div>
        <div style="font-size: 13px;">
            {group_name}
        </div>
    </div>""")

        if other_prefixes:
            html_parts.append(f"""
    {cls._prefix_note_html(other_prefixes)}""")

        html_parts.append("</div>")

        return "\n".join(html_parts)

    @classmethod
    def _build_command_detail_markdown(
        cls, cmd: Dict, prefix: str, other_prefixes: Optional[list] = None
    ) -> str:
        name = cmd["name"]
        info = cmd["info"]

        lines = [
            f"**命令详情:** `{prefix}{name}`",
            "",
            f"**描述:** {info.get('help', '暂无描述')}",
            "",
        ]

        # 别名 - 从全局 command.aliases 获取
        main_name = info.get("main_name", name)
        aliases = []
        for alias, mapped_name in command.aliases.items():
            if mapped_name == main_name and alias != main_name:
                aliases.append(alias)

        if aliases:
            aliases_text = ", ".join(f"`{prefix}{a}`" for a in aliases)
            lines.append(f"**别名:** {aliases_text}")
            lines.append("")

        # 用法
        if info.get("usage"):
            lines.append(f"**用法:** `{info['usage'].replace('/', prefix)}`")
            lines.append("")

        # 权限
        if info.get("permission"):
            lines.append("**权限:** 需要特殊权限")
            lines.append("")

        # 分组
        if info.get("group"):
            group_name = cls._get_group_name(info["group"])
            lines.append(f"**分组:** {group_name}")
            lines.append("")
        if other_prefixes:
            lines.append(f"其他触发前缀: {'、'.join(other_prefixes)}")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def _build_command_detail_text(
        cls, cmd: Dict, prefix: str, other_prefixes: Optional[list] = None
    ) -> str:
        name = cmd["name"]
        info = cmd["info"]

        lines = [
            f"命令详情: {prefix}{name}",
            "----------",
            f"描述: {info.get('help', '暂无描述')}",
            "",
        ]

        # 别名 - 从全局 command.aliases 获取
        main_name = info.get("main_name", name)
        aliases = []
        for alias, mapped_name in command.aliases.items():
            if mapped_name == main_name and alias != main_name:
                aliases.append(alias)

        if aliases:
            aliases_text = ", ".join(f"{prefix}{a}" for a in aliases)
            lines.append(f"别名: {aliases_text}")
            lines.append("")

        # 用法
        if info.get("usage"):
            lines.append(f"用法: {info['usage'].replace('/', prefix)}")
            lines.append("")

        # 权限
        if info.get("permission"):
            lines.append("权限: 需要特殊权限")
            lines.append("")

        # 分组
        if info.get("group"):
            group_name = cls._get_group_name(info["group"])
            lines.append(f"分组: {group_name}")
            lines.append("")
        if other_prefixes:
            lines.append(f"其他触发前缀: {'、'.join(other_prefixes)}")
            lines.append("")

        return "\n".join(lines)

    # ==================== 错误消息模板 ====================

    @classmethod
    def build_error(cls, title: str, message: str) -> Dict[str, str]:
        html = f"""
<div style="padding: 12px; border-radius: 8px;">
    <div style="color: {cls.ERROR_COLOR}; font-size: 14px; font-weight: bold; margin-bottom: 8px;">{title}</div>
    <div style="font-size: 13px;">{message}</div>
</div>"""

        markdown = f"**{title}**\n\n{message}"

        text = f"{title}\n\n{message}"

        return {"html": html, "markdown": markdown, "text": text}
