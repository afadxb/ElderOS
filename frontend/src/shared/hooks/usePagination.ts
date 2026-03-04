import { useState, useMemo } from 'react';

interface PaginationResult<T> {
  page: number;
  totalPages: number;
  paginatedItems: T[];
  setPage: (p: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  hasNext: boolean;
  hasPrev: boolean;
}

export function usePagination<T>(items: T[], pageSize: number = 10): PaginationResult<T> {
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));

  const paginatedItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    return items.slice(start, start + pageSize);
  }, [items, page, pageSize]);

  return {
    page,
    totalPages,
    paginatedItems,
    setPage: (p: number) => setPage(Math.max(1, Math.min(p, totalPages))),
    nextPage: () => setPage(p => Math.min(p + 1, totalPages)),
    prevPage: () => setPage(p => Math.max(p - 1, 1)),
    hasNext: page < totalPages,
    hasPrev: page > 1,
  };
}
