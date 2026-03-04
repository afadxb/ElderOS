export async function simulateLatency(): Promise<void> {
  await new Promise(r => setTimeout(r, 100 + Math.random() * 200));
}
