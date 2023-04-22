import os

import dateutil.parser
from httpx import HTTPError
from sqlalchemy import select

import api.revchatgpt
from api.database import get_async_session_context
from api.models import Conversation
from utils.logger import get_logger
from revChatGPT.typings import Error as revChatGPTError

logger = get_logger(__name__)


def get_model_name_from_conv(conversation) -> str:
    result = None
    try:
        current_node = conversation["current_node"]
        while current_node:
            node = conversation["mapping"][current_node]
            result = node["message"]["metadata"]["model_slug"]
            if result:
                break
            current_node = node["parent"]
    finally:
        return result


async def sync_conversations():
    try:
        logger.info("Syncing conversations...")
        result = await api.revchatgpt.chatgpt_manager.get_conversations()
        logger.info(f"Fetched {len(result)} conversations from ChatGPT account.")
        openai_conversations_map = {conv['id']: conv for conv in result}
        async with get_async_session_context() as session:
            r = await session.execute(select(Conversation))
            results = r.scalars().all()

            for conv_db in results:
                openai_conv = openai_conversations_map.get(conv_db.conversation_id, None)
                if openai_conv:
                    # 同步标题
                    if openai_conv["title"] != conv_db.title:
                        conv_db.title = openai_conv["title"]
                        logger.info(f"Conversation {conv_db.conversation_id} title changed: {conv_db.title}")
                    # 同步时间
                    create_time = dateutil.parser.isoparse(openai_conv["create_time"])
                    if create_time != conv_db.create_time:
                        conv_db.create_time = create_time
                        logger.info(
                            f"Conversation {conv_db.conversation_id} created time changed：{conv_db.create_time}")
                    session.add(conv_db)
                    openai_conversations_map.pop(conv_db.conversation_id)
                else:
                    if conv_db.is_valid:  # 数据库中存在，但 ChatGPT 中（可能）不存在
                        # conv_db.is_valid = False
                        logger.warning(
                            f"Cannot fetch conversation [{conv_db.title}]({conv_db.conversation_id})")
                        # session.add(conv_db)

            # 新增对话
            for openai_conv in openai_conversations_map.values():
                new_conv = Conversation(
                    conversation_id=openai_conv["id"],
                    title=openai_conv["title"],
                    is_valid=True,
                    create_time=dateutil.parser.isoparse(openai_conv["create_time"])
                )
                session.add(new_conv)
                logger.info(
                    f"Conversation [{new_conv.title}]({new_conv.conversation_id}) not recorded, added to database")

            await session.commit()
        logger.info("Sync conversations finished.")
    except revChatGPTError as e:
        logger.error(f"Fetch conversation error (ChatGPTError): {e.source} {e.code}: {e.message}")
        logger.warning("Sync conversations on startup failed!")
    except HTTPError as e:
        logger.error(f"Fetch conversation error (httpx.HTTPError): {str(e)}")
        logger.warning("Sync conversations on startup failed!")
    except Exception as e:
        logger.error(f"Fetch conversation error (unknown): {str(e)}")
        logger.warning("Sync conversations on startup failed!")