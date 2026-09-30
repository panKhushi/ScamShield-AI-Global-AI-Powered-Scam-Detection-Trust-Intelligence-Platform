"use client";

import { motion, useReducedMotion } from "framer-motion";
import { ReactNode, useEffect, useState } from "react";

export function PageTransition({ children }: { children: ReactNode }) {
    const reduceMotion = useReducedMotion();

    return (
        <motion.div
            initial={reduceMotion ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.24, ease: "easeOut" }}
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
            setDisplayValue(value);
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

    return <>{displayValue}</>;
}

export function ScanLoader() {
    return (
        <span className="inline-flex items-center gap-2">
            <motion.span
                aria-hidden="true"
                className="h-4 w-4 rounded-full border-2 border-[#06201B]/30 border-t-[#06201B]"
                animate={{ rotate: 360 }}
                transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
            />
            <span>Scanning...</span>
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
