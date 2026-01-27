/**
 * Lightweight word-level diff for showing changes
 */

export function computeWordDiff(oldText, newText) {
  if (!oldText || !newText) return { parts: [] };
  
  const oldWords = tokenize(oldText);
  const newWords = tokenize(newText);
  
  const diff = lcs(oldWords, newWords);
  
  return { parts: diff };
}

function tokenize(text) {
  // Split by spaces but keep punctuation attached to words
  return text.trim().split(/\s+/);
}

/**
 * Longest Common Subsequence based diff
 */
function lcs(arr1, arr2) {
  const m = arr1.length;
  const n = arr2.length;
  
  // Build LCS table
  const dp = Array(m + 1).fill(0).map(() => Array(n + 1).fill(0));
  
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (arr1[i - 1] === arr2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }
  
  // Backtrack to find diff
  const result = [];
  let i = m, j = n;
  
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && arr1[i - 1] === arr2[j - 1]) {
      result.unshift({ type: 'equal', value: arr1[i - 1] });
      i--;
      j--;
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      result.unshift({ type: 'added', value: arr2[j - 1] });
      j--;
    } else if (i > 0) {
      result.unshift({ type: 'removed', value: arr1[i - 1] });
      i--;
    }
  }
  
  return result;
}

/**
 * Merge consecutive parts of the same type for cleaner rendering
 */
export function mergeDiffParts(parts) {
  if (!parts || parts.length === 0) return [];
  
  const merged = [];
  let current = { ...parts[0], words: [parts[0].value] };
  
  for (let i = 1; i < parts.length; i++) {
    if (parts[i].type === current.type) {
      current.words.push(parts[i].value);
    } else {
      merged.push({ ...current, text: current.words.join(' ') });
      current = { ...parts[i], words: [parts[i].value] };
    }
  }
  
  merged.push({ ...current, text: current.words.join(' ') });
  return merged;
}
