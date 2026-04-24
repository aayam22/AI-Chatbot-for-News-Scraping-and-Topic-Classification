import { useEffect, useRef } from 'react';

/**
 * Custom hook for auto-scrolling to the newest active message.
 * It scrolls when a new query/loading bubble is appended and again
 * when that loading message becomes the final response, aligning the
 * top of the latest message into view instead of jumping to the end.
 */
export const useAutoScroll = (messages) => {
  const lastMessageRef = useRef(null);
  const previousStateRef = useRef({
    count: 0,
    lastMessageId: null,
    lastMessageLoading: false
  });

  useEffect(() => {
    const safeMessages = Array.isArray(messages) ? messages : [];
    const currentCount = safeMessages.length;
    const lastMessage = currentCount > 0 ? safeMessages[currentCount - 1] : null;
    const previousState = previousStateRef.current;

    const hasNewMessage = currentCount > previousState.count;
    const lastMessageChanged =
      previousState.count > 0 &&
      lastMessage &&
      previousState.lastMessageId !== lastMessage.id;
    const responseCompleted =
      lastMessage &&
      previousState.lastMessageId === lastMessage.id &&
      previousState.lastMessageLoading &&
      !lastMessage.loading;

    if (hasNewMessage || lastMessageChanged || responseCompleted) {
      lastMessageRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }

    previousStateRef.current = {
      count: currentCount,
      lastMessageId: lastMessage?.id ?? null,
      lastMessageLoading: Boolean(lastMessage?.loading)
    };
  }, [messages]);

  return lastMessageRef;
};

export default useAutoScroll;
