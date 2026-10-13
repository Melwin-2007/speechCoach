/**
 * Greedy vertical lane assignment for overlapping time intervals.
 * Used for placing flaw region badges so they do not collide or stack destructively.
 * 
 * @param {Array<{start: number, end: number, id: string}>} items
 * @param {number} minGapSeconds Minimum gap between consecutive items in the same lane
 * @returns {Array<{...item, lane: number}>} Items augmented with 0-indexed lane number
 */
export function assignLanes(items = [], minGapSeconds = 0.5, duration = 60) {
  if (!items || items.length === 0) return [];

  // Sort primarily by start time
  const sorted = [...items].sort((a, b) => a.start - b.start);

  // Each badge has a minimum readable width of ~120px, which on a typical ~800px waveform
  // corresponds to ~12-14% of the duration. We reserve this horizontal footprint to prevent overlapping.
  const visualFootprintSec = Math.max(minGapSeconds, (duration || 60) * 0.13);

  const laneEndTimes = [];

  return sorted.map((item) => {
    const itemVisualEnd = Math.max(item.end, item.start + visualFootprintSec);
    let assignedLane = -1;

    for (let i = 0; i < laneEndTimes.length; i++) {
      if (item.start >= laneEndTimes[i]) {
        assignedLane = i;
        laneEndTimes[i] = itemVisualEnd;
        break;
      }
    }

    if (assignedLane === -1) {
      assignedLane = laneEndTimes.length;
      laneEndTimes.push(itemVisualEnd);
    }

    return {
      ...item,
      lane: assignedLane,
    };
  });
}
