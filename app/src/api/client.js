/**
 * @file client.js - API client for SpeechCoach backend
 */

const API_BASE = "";

/**
 * Validates that an AnalysisResult strictly conforms to CONTRACTS.md Section 6.
 * @param {any} result
 * @returns {boolean}
 */
export function validateResult(result) {
  if (!result || typeof result !== "object") return false;
  if (!result.meta || !result.words || !result.scores) return false;
  if (!Array.isArray(result.words) || !Array.isArray(result.flaws)) return false;

  // Verify series array lengths if series data exists
  if (result.series && Array.isArray(result.series.t)) {
    const tLen = result.series.t.length;
    if (result.series.participant) {
      for (const key of ["pitch_st", "energy_db", "rate_sps"]) {
        const arr = result.series.participant[key];
        if (Array.isArray(arr) && arr.length !== tLen) {
          console.warn(`Series participant.${key} length (${arr.length}) != t length (${tLen})`);
          return false;
        }
      }
    }
    if (result.series.baseline) {
      for (const key of ["pitch_st", "pitch_lo", "pitch_hi", "energy_db", "rate_sps"]) {
        const arr = result.series.baseline[key];
        if (Array.isArray(arr) && arr.length !== tLen) {
          console.warn(`Series baseline.${key} length (${arr.length}) != t length (${tLen})`);
          return false;
        }
      }
    }
  }

  // Verify flaws are sorted non-decreasingly by start time
  for (let i = 1; i < result.flaws.length; i++) {
    if (result.flaws[i].start < result.flaws[i - 1].start) {
      console.warn(`Flaws out of order at index ${i}`);
      return false;
    }
  }

  return true;
}

/**
 * Normalizes HTTP or network errors into user-friendly error objects.
 * @param {any} err
 * @param {number} [status]
 * @returns {{ kind: string, message: string, status?: number }}
 */
function normalizeError(err, status) {
  if (err && err.name === "AbortError") {
    return {
      kind: "timeout",
      message: "The analysis request timed out after 120 seconds. Please try a shorter audio clip.",
      status: 408,
    };
  }

  const msg = err && err.message ? err.message : String(err);

  if (status === 413 || msg.includes("25 MB") || msg.includes("too large")) {
    return {
      kind: "too_large",
      message: "Audio file exceeds 25 MB limit. Please select a smaller recording.",
      status: 413,
    };
  }

  if (status === 422) {
    return {
      kind: "validation",
      message: "The request parameters failed validation. Please check your transcript.",
      status: 422,
    };
  }

  if (status === 400) {
    if (msg.toLowerCase().includes("transcript")) {
      return {
        kind: "transcript",
        message: msg || "Please provide a valid spoken transcript.",
        status: 400,
      };
    }
    return {
      kind: "audio",
      message: msg || "Could not read audio file. Please check the file format.",
      status: 400,
    };
  }

  if (!status || msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
    return {
      kind: "network",
      message: "Unable to reach the SpeechCoach server. Please check your connection.",
      status: 0,
    };
  }

  return {
    kind: "server",
    message: msg || "An unexpected error occurred during speech analysis.",
    status: status || 500,
  };
}

/**
 * Fetch list of available baseline models.
 * @returns {Promise<Array<{ id: string, title: string, n_ideals: number }>>}
 */
export async function getBaselines() {
  try {
    const res = await fetch(`${API_BASE}/baselines`);
    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn("Failed to fetch baselines from backend, using fallback list:", err);
    return [
      { id: "T1", title: "Indian Pep Talk", n_ideals: 1 },
      { id: "T2", title: "Martin Luther King Jr. - I Have a Dream", n_ideals: 1 },
      { id: "T3", title: "Dr. A.P.J. Abdul Kalam", n_ideals: 1 },
      { id: "T4", title: "Tagore - Where the mind is without fear", n_ideals: 2 },
    ];
  }
}

/**
 * Fetch a precomputed demo result.
 * @param {string} name - 'ideal' | 'almost' | 'botched'
 * @returns {Promise<any>}
 */
export async function getDemo(name) {
  const url = `/demo/${name}`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Could not load demo '${name}' (HTTP ${res.status})`);
    }
    const json = await res.json();
    if (!validateResult(json)) {
      throw new Error("Demo data failed validation check.");
    }
    return json;
  } catch (err) {
    // Fallback to static public folder
    const fallbackRes = await fetch(`/demo/${name}.json`);
    if (fallbackRes.ok) {
      return await fallbackRes.json();
    }
    throw normalizeError(err);
  }
}

/**
 * Upload audio file and transcript for analysis.
 * @param {object} params
 * @param {File|Blob} params.file
 * @param {string} params.transcript
 * @param {string} [params.baselineId]
 * @param {string} [params.mode]
 * @param {AbortSignal} [params.signal]
 * @returns {Promise<any>}
 */
export async function analyze({ file, transcript, baselineId = "auto", mode = "auto", signal }) {
  if (!file) {
    throw { kind: "audio", message: "Please select an audio file to analyze." };
  }
  if (!transcript || transcript.trim().length === 0) {
    throw { kind: "transcript", message: "Please enter or paste the speech transcript." };
  }

  const formData = new FormData();
  formData.append("audio", file);
  formData.append("transcript", transcript.trim());
  if (baselineId && baselineId !== "auto") {
    formData.append("baseline_id", baselineId);
  }
  formData.append("mode", mode);

  // Setup 120s timeout controller if no custom signal
  let timeoutId = null;
  let activeSignal = signal;
  if (!activeSignal) {
    const controller = new AbortController();
    timeoutId = setTimeout(() => controller.abort(), 120000);
    activeSignal = controller.signal;
  }

  try {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      body: formData,
      signal: activeSignal,
    });

    if (timeoutId) clearTimeout(timeoutId);

    if (!res.ok) {
      let errorMsg = `Server error (HTTP ${res.status})`;
      try {
        const errorJson = await res.json();
        if (errorJson && errorJson.error) {
          errorMsg = errorJson.error;
        }
      } catch {
        // Fall back to default errorMsg
      }
      throw normalizeError(new Error(errorMsg), res.status);
    }

    const data = await res.json();
    if (!validateResult(data)) {
      throw {
        kind: "invalid_response",
        message: "Analysis results received from server did not match the required data schema.",
        status: 502,
      };
    }

    return data;
  } catch (err) {
    if (timeoutId) clearTimeout(timeoutId);
    if (err.kind) throw err;
    throw normalizeError(err);
  }
}
