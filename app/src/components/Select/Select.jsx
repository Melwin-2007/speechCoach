import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Check, Sparkles, BookOpen, Globe, ArrowRight } from "lucide-react";
import styles from "./Select.module.css";

const DEFAULT_OPTIONS = [
  {
    id: "auto",
    title: "Auto-detect matching baseline",
    desc: "Automatically maps text to closest reference speech or population norms",
    badge: "Recommended",
    badgeType: "mint",
    icon: Sparkles,
  },
  {
    id: "T01",
    title: "T01 — Technology & Communication",
    desc: "Conversational speed & articulation · 109 words",
    badge: "Reference Standard",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T02",
    title: "T02 — Modern Education",
    desc: "Measured educational delivery · 112 words",
    badge: "Reference Standard",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T03",
    title: "T03 — Environmental Responsibility",
    desc: "Persuasive rhetorical cadence · 105 words",
    badge: "Reference Standard",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T04",
    title: "T04 — Artificial Intelligence",
    desc: "Structured presentation pacing · 117 words",
    badge: "Reference Standard",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T05",
    title: "T05 — Public Speaking & Delivery",
    desc: "Formal speech modulation baseline · 115 words",
    badge: "Reference Standard",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T06",
    title: "T06 — Innovation & Problem Solving",
    desc: "Inspirational dynamic delivery · 118 words",
    badge: "Reference Standard",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T07",
    title: "T07 — Teamwork & Collaboration",
    desc: "Collaborative conversational cadence · 122 words",
    badge: "Reference Standard",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T08",
    title: "T08 — The Future & Decision Making",
    desc: "Reflective oratorical cadence · 114 words",
    badge: "Reference Standard",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "prior",
    title: "Other speech, no reference (General Norms)",
    desc: "Evaluate against general population speaking benchmarks",
    badge: "Universal",
    badgeType: "butter",
    icon: Globe,
    isSpecial: true,
  },
];

export default function Select({ value, onChange, options = DEFAULT_OPTIONS }) {
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  const containerRef = useRef(null);
  const listRef = useRef(null);

  const selectedOption = options.find((opt) => opt.id === value) || options[0];

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (e) => {
      if (!isOpen) {
        if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
          e.preventDefault();
          setIsOpen(true);
        }
        return;
      }

      if (e.key === "Escape") {
        e.preventDefault();
        setIsOpen(false);
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setHighlightedIndex((prev) => (prev + 1) % options.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setHighlightedIndex((prev) => (prev - 1 + options.length) % options.length);
      } else if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        const opt = options[highlightedIndex];
        if (opt) {
          onChange(opt.id);
          setIsOpen(false);
        }
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, highlightedIndex, options, onChange]);

  // Ensure scroll is at top when opening
  useEffect(() => {
    if (isOpen && listRef.current) {
      listRef.current.scrollTop = 0;
    }
  }, [isOpen]);

  const handleSelect = (id) => {
    onChange(id);
    setIsOpen(false);
  };

  return (
    <div className={styles.selectContainer} ref={containerRef}>
      {/* Trigger Button */}
      <button
        type="button"
        className={`${styles.triggerBtn} ${isOpen ? styles.triggerBtnOpen : ""}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <div className={styles.triggerContent}>
          <div className={styles.triggerIconWrap}>
            {selectedOption.icon && <selectedOption.icon size={15} className={styles.triggerIcon} />}
          </div>
          <div className={styles.triggerTextCol}>
            <span className={styles.triggerTitle}>{selectedOption.title}</span>
            <span className={styles.triggerSub}>{selectedOption.badge}</span>
          </div>
        </div>
        <div className={`${styles.chevronWrap} ${isOpen ? styles.chevronOpen : ""}`}>
          <ChevronDown size={16} />
        </div>
      </button>

      {/* Floating Popover Dropdown */}
      {isOpen && (
        <div className={styles.popoverMenu} role="listbox" tabIndex={-1}>
          <div className={styles.optionsList} ref={listRef}>
            {options.map((opt, idx) => {
              const isSelected = opt.id === value;
              const isHighlighted = idx === highlightedIndex;
              const IconComp = opt.icon || BookOpen;

              return (
                <React.Fragment key={opt.id}>
                  {opt.isSpecial && <div className={styles.optionDivider} />}
                  <div
                    className={`${styles.optionTile} ${isSelected ? styles.optionTileSelected : ""} ${
                      isHighlighted ? styles.optionTileHighlighted : ""
                    }`}
                    role="option"
                    aria-selected={isSelected}
                    onClick={() => handleSelect(opt.id)}
                    onMouseEnter={() => setHighlightedIndex(idx)}
                  >
                    <div className={styles.optionIconCircle}>
                      <IconComp size={15} />
                    </div>

                    <div className={styles.optionTextCol}>
                      <span className={styles.optionTitle}>{opt.title}</span>
                      <span className={styles.optionDesc}>{opt.desc}</span>
                    </div>

                    <div className={styles.optionMetaGroup}>
                      {opt.badge && (
                        <span
                          className={`${styles.badge} ${
                            opt.badgeType === "mint"
                              ? styles.badgeMint
                              : opt.badgeType === "butter"
                              ? styles.badgeButter
                              : styles.badgePaper
                          }`}
                        >
                          {opt.badge}
                        </span>
                      )}

                      <div className={styles.indicatorWrap}>
                        {isSelected ? (
                          <div className={styles.checkCircle}>
                            <Check size={11} strokeWidth={3} />
                          </div>
                        ) : (
                          <ArrowRight size={13} className={styles.hoverArrow} />
                        )}
                      </div>
                    </div>
                  </div>
                </React.Fragment>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
