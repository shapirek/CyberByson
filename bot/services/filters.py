from typing import List, Dict

async def get_receivers_async(
    users_data: List[Dict],
    recipient_type: str,
    sender_id: str,
    **kwargs
) -> List[str]:
    """
    Фильтрует список users_data по типу получателя.
    """
    predicates = {
        'direction': lambda u: u.get('направление') == kwargs.get('direction'),
        'team':      lambda u: u.get('команда') == kwargs.get('team'),
        'director':  lambda u: u.get('статус') == '0',
        'all_staff': lambda u: bool(u.get('id')),
        'tournament_judges': lambda u: (
            u.get('судья') == '1' and u.get('направление') in kwargs.get('directions', [])
        ),
    }

    pred = predicates.get(recipient_type, lambda u: False)
    return [
        str(u['id']) for u in users_data
        if pred(u) and str(u['id']) != str(sender_id)
    ]
