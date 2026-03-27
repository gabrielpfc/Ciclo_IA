import { useEffect, useRef } from 'react';

export default function AudioVisualizer({ stream }: { stream: MediaStream | null }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!stream || !canvasRef.current) return;
    
    const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const analyser = audioCtx.createAnalyser();
    const source = audioCtx.createMediaStreamSource(stream);
    source.connect(analyser);
    
    analyser.fftSize = 256;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    
    let drawVisual: number;

    const draw = () => {
      drawVisual = requestAnimationFrame(draw);
      analyser.getByteFrequencyData(dataArray);
      
      if (!canvasCtx) return;
      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
      
      const barWidth = (canvas.width / bufferLength) * 2.5;
      let x = 0;
      
      for (let i = 0; i < bufferLength; i++) {
        const barHeight = dataArray[i] / 2;
        canvasCtx.fillStyle = `rgb(52, 211, 153)`; // Emerald 400
        canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
        x += barWidth + 1;
      }
    };
    
    draw();
    return () => { cancelAnimationFrame(drawVisual); audioCtx.close(); };
  }, [stream]);

  return <canvas ref={canvasRef} width="150" height="40" className="bg-slate-900/50 rounded-lg border border-emerald-500/20" />;
}
