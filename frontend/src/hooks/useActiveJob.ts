import { useEffect, useRef, useState } from 'react';
import { getJob, getJobLogs, JobResponse } from '../api/jobs';

export function useActiveJob(pollInterval = 2000) {
  const [activeJob, setActiveJob] = useState<JobResponse | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const timerRef = useRef<number | null>(null);

  const startMonitoring = async (jobId: string) => {
    if (!jobId) return;
    try {
      const j = await getJob(jobId);
      setActiveJob(j);
      const l = await getJobLogs(jobId, 300);
      setLogs(l.lines);
    } catch (err) {
      // swallow for now
    }

    if (timerRef.current) window.clearInterval(timerRef.current);
    timerRef.current = window.setInterval(async () => {
      if (!jobId) return;
      try {
        const latest = await getJob(jobId);
        setActiveJob(latest);
        const l = await getJobLogs(jobId, 300);
        setLogs(l.lines);
      } catch (e) {
        // ignore transient errors
      }
    }, pollInterval) as unknown as number;
  };

  const stopMonitoring = () => {
    if (timerRef.current) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  useEffect(() => {
    const stored = localStorage.getItem('invest_active_job_id');
    if (stored) startMonitoring(stored);
    return () => stopMonitoring();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { activeJob, logs, startMonitoring, stopMonitoring, setActiveJob, setLogs };
}
