import type { LoopDetectionResult } from '../types/index.ts';

export class LoopDetector {
  private history: string[] = [];

  public analyze(input: string): LoopDetectionResult {
    const trimmed = input.trim();
    if (!trimmed) return { isLoop: false, similarityScore: 0 };

    this.history.push(trimmed);
    if (this.history.length > 50) this.history.shift();

    // Check repetition count
    const recent = this.history.slice(-5);
    const count = recent.filter(x => x === trimmed).length;

    if (count >= 3) {
      return {
        isLoop: true,
        reason: 'Detected repeated identical input 3 or more times consecutively.',
        repeatedPattern: trimmed,
        similarityScore: 1.0
      };
    }

    return {
      isLoop: false,
      similarityScore: 0.0
    };
  }

  public clear(): void {
    this.history = [];
  }
}
