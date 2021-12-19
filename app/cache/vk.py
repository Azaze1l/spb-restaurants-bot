from app.cache import get_state_cache
from app.helpers.vkontakte import get_photo_attachment


async def get_photo_by_link(photo_link):
    state_cache_service = get_state_cache()
    state_data = await state_cache_service.get_cache(photo_link)
    if state_data is None:
        state_data = await get_photo_attachment(photo_link)
        await state_cache_service.set_cache(photo_link, state_data)
        return state_data
    return state_data
