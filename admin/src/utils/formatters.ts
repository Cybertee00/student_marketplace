export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-ZA', {
    style: 'currency',
    currency: 'ZAR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

export const formatDate = (date: string | Date): string => {
  return new Date(date).toLocaleDateString('en-ZA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (date: string | Date): string => {
  return new Date(date).toLocaleString('en-ZA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatTime = (date: string | Date): string => {
  return new Date(date).toLocaleTimeString('en-ZA', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-ZA').format(num);
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

export const formatMessageTime = (date: string | Date): string => {
  const messageDate = new Date(date);
  
  // Convert UTC time to South African time (UTC+2)
  const southAfricanTime = new Date(messageDate.getTime() + (2 * 60 * 60 * 1000));
  
  // Format time as HH:mm (24-hour format)
  const hours = southAfricanTime.getHours().toString().padStart(2, '0');
  const minutes = southAfricanTime.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
};