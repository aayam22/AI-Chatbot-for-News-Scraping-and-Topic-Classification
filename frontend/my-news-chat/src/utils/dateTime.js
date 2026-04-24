function normalizeServerTimestamp(value) {
  if (!value) {
    return null;
  }

  if (value instanceof Date) {
    return value;
  }

  const stringValue = String(value);
  const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(stringValue);
  const normalizedValue = hasTimezone ? stringValue : `${stringValue}Z`;
  const parsedDate = new Date(normalizedValue);

  return Number.isNaN(parsedDate.getTime()) ? null : parsedDate;
}

export function formatMessageTime(value, locale = 'en-US') {
  const date = normalizeServerTimestamp(value);

  if (!date) {
    return '';
  }

  return date.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function formatMessageDate(value, locale = 'en-US') {
  const date = normalizeServerTimestamp(value);

  if (!date) {
    return '';
  }

  return date.toLocaleDateString(locale, {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

export function formatMessageDateShort(value, locale = 'en-US') {
  const date = normalizeServerTimestamp(value);

  if (!date) {
    return '';
  }

  return date.toLocaleDateString(locale, {
    month: 'short',
    day: 'numeric'
  });
}

export function formatMessageDateTime(value, locale = 'en-US') {
  const date = normalizeServerTimestamp(value);

  if (!date) {
    return '';
  }

  return date.toLocaleString(locale, {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function sortMessagesNewestFirst(messages) {
  return [...messages].sort((a, b) => {
    const aTime = normalizeServerTimestamp(a.created_at)?.getTime() ?? 0;
    const bTime = normalizeServerTimestamp(b.created_at)?.getTime() ?? 0;

    if (bTime !== aTime) {
      return bTime - aTime;
    }

    return (b.id ?? 0) - (a.id ?? 0);
  });
}

export function sortMessagesOldestFirst(messages) {
  return [...messages].sort((a, b) => {
    const aTime = normalizeServerTimestamp(a.created_at)?.getTime() ?? 0;
    const bTime = normalizeServerTimestamp(b.created_at)?.getTime() ?? 0;

    if (aTime !== bTime) {
      return aTime - bTime;
    }

    return (a.id ?? 0) - (b.id ?? 0);
  });
}

export function buildConversationTurns(messages) {
  const chronologicalMessages = sortMessagesOldestFirst(messages);
  const turns = [];
  let pendingUser = null;

  chronologicalMessages.forEach((message) => {
    if (message.role === 'user') {
      if (pendingUser) {
        turns.push({
          id: `turn-user-${pendingUser.id}`,
          user: pendingUser,
          assistant: null,
          created_at: pendingUser.created_at
        });
      }

      pendingUser = message;
      return;
    }

    if (message.role === 'assistant') {
      if (pendingUser) {
        turns.push({
          id: `turn-${pendingUser.id}-${message.id}`,
          user: pendingUser,
          assistant: message,
          created_at: message.created_at || pendingUser.created_at
        });
        pendingUser = null;
        return;
      }

      turns.push({
        id: `turn-assistant-${message.id}`,
        user: null,
        assistant: message,
        created_at: message.created_at
      });
    }
  });

  if (pendingUser) {
    turns.push({
      id: `turn-user-${pendingUser.id}`,
      user: pendingUser,
      assistant: null,
      created_at: pendingUser.created_at
    });
  }

  return turns.sort((a, b) => {
    const aTime = normalizeServerTimestamp(a.created_at)?.getTime() ?? 0;
    const bTime = normalizeServerTimestamp(b.created_at)?.getTime() ?? 0;

    if (bTime !== aTime) {
      return bTime - aTime;
    }

    return String(b.id).localeCompare(String(a.id));
  });
}

export { normalizeServerTimestamp };
