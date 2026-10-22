"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ReactNode, useEffect, useState } from "react";

export function PageTransition({ children }: { children: ReactNode }) {
    const reduceMotion = useReducedMotion();

    return (
        <motion.div
            initial={reduceMotion ? false : { opacity: 0, y: 14, filter: "blur(4px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{ duration: 0.42, ease: [0.22, 1, 0.36, 1] }}
            className="flex min-h-0 flex-1 flex-col"
        >
            {children}
        </motion.div>
    );
}

export function AnimatedNumber({ value }: { value: number }) {
    const reduceMotion = useReducedMotion();
    const [displayValue, setDisplayValue] = useState(reduceMotion ? value : 0);

    useEffect(() => {
        if (reduceMotion) {
            return;
        }

        const start = performance.now();
        const duration = 360;
        let frame = 0;
        const update = (now: number) => {
            const progress = Math.min((now - start) / duration, 1);
            setDisplayValue(Math.round(value * (1 - Math.pow(1 - progress, 3))));
            if (progress < 1) frame = requestAnimationFrame(update);
        };
        frame = requestAnimationFrame(update);
        return () => cancelAnimationFrame(frame);
    }, [reduceMotion, value]);

    return <>{reduceMotion ? value : displayValue}</>;
}

export function ScanLoader() {
    return (
        <span className="inline-flex items-center gap-2" role="status" aria-live="polite">
            <motion.span
                aria-hidden="true"
                className="h-4 w-4 rounded-full border-2 border-[#06201B]/30 border-t-[#06201B]"
                animate={{ rotate: 360 }}
                transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
            />
            <span>Scanning securely...</span>
        </span>
    );
}

export const revealItem = {
    hidden: { opacity: 0, y: 8 },
    visible: { opacity: 1, y: 0 },
};

export const revealGroup = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.06 } },
};
