/**
 * Greedy vertical lane assignment for overlapping time intervals.
 * Used for placing flaw region badges so they do not collide or stack destructively.
 * 
 * @param {Array<{start: number, end: number, id: string}>} items
 * @param {number} minGapSeconds Minimum gap between consecutive items in the same lane
 * @returns {Array<{...item, lane: number}>} Items augmented with 0-indexed lane number
 */
export function assignLanes(items = [], minGapSeconds = 0.2) {
  if (!items || items.length === 0) return [];

  // Sort primarily by start time, secondarily by duration descending
  const sorted = [...items].sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    return (b.end - b.start) - (a.end - a.start);
  });

  // Track the end time of the last item in each lane
  const laneEndTimes = [];

  return sorted.map((item) => {
    let assignedLane = -1;

    for (let i = 0; i < laneEndTimes.length; i++) {
      if (item.start >= laneEndTimes[i] + minGapSeconds) {
        assignedLane = i;
        laneEndTimes[i] = item.end;
        break;
      }
    }

    if (assignedLane === -1) {
      assignedLane = laneEndTimes.length;
      laneEndTimes.push(item.end);
    }

    return {
      ...item,
      lane: assignedLane,
    };
  });
}
