import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, Check, Sparkles, BookOpen, Globe, ArrowRight } from "lucide-react";
import styles from "./Select.module.css";

const DEFAULT_OPTIONS = [
  {
    id: "auto",
    title: "Auto-detect matching baseline",
    desc: "Automatically maps text to closest reference speech",
    badge: "Recommended",
    badgeType: "mint",
    icon: Sparkles,
  },
  {
    id: "T1",
    title: "T1 — Indian Pep Talk",
    desc: "Indian English conversational delivery · 302 words",
    badge: "Indian English",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T2",
    title: "T2 — Martin Luther King Jr. \"I Have a Dream\"",
    desc: "Iconic oratorical cadence and emphasis · 388 words",
    badge: "American Oratory",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T3",
    title: "T3 — Dr. A.P.J. Abdul Kalam",
    desc: "Deliberate rhythmic speech & pause structure · 391 words",
    badge: "Indian English",
    badgeType: "paper",
    icon: BookOpen,
  },
  {
    id: "T4",
    title: "T4 — Abraham Lincoln \"Gettysburg Address\"",
    desc: "Formal ceremonial cadence & pacing baseline · 270 words",
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
