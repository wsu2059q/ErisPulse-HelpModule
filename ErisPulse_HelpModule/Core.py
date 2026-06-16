from typing import Dict, List, Optional

from ErisPulse import sdk
from ErisPulse.Core import config
from ErisPulse.Core.Bases import BaseModule
from ErisPulse.Core.Event import command

from .templates import HelpTemplates


class HelpModule(BaseModule):
    def __init__(self):
        self.sdk = sdk
        self.logger = sdk.logger.get_child("HelpModule")
        self.command_list = []
        self.command_map = {}

    @staticmethod
    def should_eager_load():
        return True

    async def on_load(self, event):
        self._register_commands()
        self.logger.info("HelpModule 已加载")
        return True

    async def on_unload(self, event):
        self._unregister_commands()
        self.logger.info("HelpModule 已卸载")
        return True

    def _get_config(self):
        module_config = config.getConfig("HelpModule")
        if not module_config:
            default_config = {"show_hidden_commands": False, "group_commands": True}
            config.setConfig("HelpModule", default_config)
            self.logger.warning("未找到HelpModule配置，已创建默认配置")
            return default_config
        return module_config

    def _get_command_prefix(self) -> str:
        event_config = config.getConfig("ErisPulse.event", {})
        command_config = event_config.get("command", {})
        return command_config.get("prefix", "/")

    def _register_commands(self):
        self.help_command_func = self._create_help_command()
        command(
            "help",
            aliases=["h", "帮助"],
            help="显示帮助信息",
            usage="help [序号] - 显示命令列表或查看指定序号的命令详情",
        )(self.help_command_func)

    def _unregister_commands(self):
        if hasattr(self, "help_command_func"):
            command.unregister(self.help_command_func)

    def _create_help_command(self):
        async def help_command(event):
            await self._handle_help_command(event)

        return help_command

    def _build_command_list(self) -> List[Dict]:
        self.command_list = []
        module_config = self._get_config()
        show_hidden = module_config.get("show_hidden_commands", False)

        if show_hidden:
            all_commands = command.get_commands()
            for cmd_name in all_commands:
                cmd_info = command.get_command(cmd_name)
                if cmd_info and cmd_name == cmd_info.get("main_name"):
                    self.command_list.append({"name": cmd_name, "info": cmd_info})
        else:
            visible_commands = command.get_visible_commands()
            for cmd_name in visible_commands:
                cmd_info = command.get_command(cmd_name)
                if cmd_info and cmd_name == cmd_info.get("main_name"):
                    self.command_list.append({"name": cmd_name, "info": cmd_info})

        return self.command_list

    def _group_commands_by_category(self, commands: List[Dict]) -> Dict[str, List]:
        grouped = {}
        for cmd in commands:
            group = cmd["info"].get("group") or "default"
            if group not in grouped:
                grouped[group] = []
            grouped[group].append(cmd)
        return grouped

    async def _handle_help_command(self, event) -> None:
        try:
            platform = event.get_platform()
            args = event.get_command_args()

            commands = self._build_command_list()
            module_config = self._get_config()

            if args:
                # 显示命令详情
                try:
                    index = int(args[0])
                    if index in self.command_map:
                        # 使用模板构建命令详情
                        templates = HelpTemplates.build_command_detail(
                            self.command_map[index], self._get_command_prefix()
                        )
                    else:
                        # 使用错误模板
                        templates = HelpTemplates.build_error(
                            "序号超出范围", f"请输入 1-{len(commands)} 之间的序号"
                        )
                except ValueError:
                    templates = HelpTemplates.build_error(
                        "参数错误", "请输入有效的序号"
                    )
            else:
                # 显示命令列表
                templates = HelpTemplates.build_help_list(
                    commands,
                    self.command_map,
                    self._get_command_prefix(),
                    module_config.get("group_commands", True),
                )

            # 根据平台能力选择最佳格式，通过 event.reply 发送
            # event.reply 内部自动解析会话类型（含 channel/guild/thread 等）
            format_name, content = self._select_best_format(platform, templates)
            await event.reply(content, method=format_name)
        except Exception as e:
            self.logger.error(f"处理帮助命令时出错: {e}", exc_info=True)

    def _select_best_format(self, platform: str, templates: Dict[str, str]) -> tuple:
        """
        根据平台支持的发送方法选择最佳格式
        优先使用 list_sends，不支持时使用 hasattr 兜底

        返回: (format_name, content)
        """
        # 首先尝试使用 list_sends（推荐方式）
        try:
            supported_methods = sdk.adapter.list_sends(platform)

            # 优先级: Html > Markdown > Text
            if "Html" in supported_methods:
                return ("Html", templates["html"])
            elif "Markdown" in supported_methods:
                return ("Markdown", templates["markdown"])
            else:
                return ("Text", templates["text"])
        except Exception as e:
            self.logger.warning(f"list_sends 检测失败: {e}，尝试使用 hasattr 兜底")

            # 使用 hasattr 作为兜底方案
            adapter = getattr(sdk.adapter, platform)
            send_obj = adapter.Send if hasattr(adapter, "Send") else None

            if send_obj is None:
                self.logger.warning(f"平台 {platform} 不支持 Send 接口，使用纯文本格式")
                return ("Text", templates["text"])

            # 检查支持的方法
            if hasattr(send_obj, "Html"):
                return ("Html", templates["html"])
            elif hasattr(send_obj, "Markdown"):
                return ("Markdown", templates["markdown"])
            else:
                return ("Text", templates["text"])
