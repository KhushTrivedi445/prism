/**
 * Date and Timezone utility for PRISM.
 * Explicitly converts canonical UTC ISO-8601 timestamps to India Standard Time (Asia/Kolkata).
 */

export function formatToIST(isoString, includeSeconds = true) {
  if (!isoString) return 'N/A';
  try {
    let s = String(isoString).trim();
    // If naive ISO string without timezone indicator, interpret as UTC
    if (!s.endsWith('Z') && !s.includes('+') && !/[-+]\d{2}:\d{2}$/.test(s)) {
      s = `${s}Z`;
    }
    const date = new Date(s);
    if (isNaN(date.getTime())) return isoString;

    return new Intl.DateTimeFormat('en-IN', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      ...(includeSeconds ? { second: '2-digit' } : {}),
      hour12: true,
    }).format(date);
  } catch (err) {
    return isoString;
  }
}
