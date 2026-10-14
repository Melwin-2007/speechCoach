import React from "react";
import { GraduationCap, Database, Activity, Layout, FileText } from "lucide-react";
import styles from "./About.module.css";

const TEAM_MEMBERS = [
  {
    name: "Aditya Patange",
    degree: "B.Tech CSE, VTU Belagavi",
    role: "Data Engineer",
    icon: Database,
    description: "Took care of the audio conversion, transcript alignment, and the flaw dataset generation.",
    image: "/team/aditya.jpeg",
    initials: "AP",
    tint: "var(--c-energy-tint)",
    accent: "var(--c-energy)",
  },
  {
    name: "Melwin Fernandes",
    degree: "B.Tech CSE, VTU Belagavi",
    role: "Signal / Analysis Engineer",
    icon: Activity,
    description: "Took care of the model training and flaw detection algorithms.",
    image: "/team/melwin.jpg",
    initials: "MF",
    tint: "var(--c-pitch-tint)",
    accent: "var(--c-pitch)",
  },
  {
    name: "Sagar Hulikavi",
    degree: "B.Tech CSE, VTU Belagavi",
    role: "App / Platform / Delivery",
    icon: Layout,
    description: "Made the website, interactive visualization dashboard, and all UI components.",
    image: "/team/sagar.jpg",
    initials: "SH",
    tint: "var(--c-pacing-tint)",
    accent: "var(--c-pacing)",
  },
  {
    name: "Pritam Shetty",
    degree: "B.Tech CSE, VTU Belagavi",
    role: "Dataset Management & Documentation",
    icon: FileText,
    description: "Dataset management, recording protocols, quality control, and project documentation.",
    image: "/team/pritam.jpg",
    initials: "PS",
    tint: "var(--c-emphasis-tint)",
    accent: "var(--c-emphasis)",
  },
];

export default function AboutTeam() {
  return (
    <div className={styles.sectionBlock}>
      <div className={styles.sectionHeader}>
        <div className={styles.badgePill}>
          <GraduationCap size={16} />
          <span>Our Team</span>
        </div>
        <h2 className={styles.sectionTitle}>Meet the Builders</h2>
        <p className={styles.sectionSubtitle}>
          Student engineers from Visvesvaraya Technological University (VTU) Belagavi building next-generation contrastive speech analytics.
        </p>
      </div>

      <div className={styles.teamGrid}>
        {TEAM_MEMBERS.map((member) => {
          const IconComp = member.icon;
          return (
            <div key={member.name} className={styles.memberCard}>
              <div className={styles.memberAvatarContainer}>
                {member.image ? (
                  <img
                    src={member.image}
                    alt={member.name}
                    className={styles.memberPhoto}
                    onError={(e) => {
                      e.currentTarget.style.display = "none";
                      const fallback = e.currentTarget.nextSibling;
                      if (fallback) fallback.style.display = "flex";
                    }}
                  />
                ) : null}
                <div
                  className={styles.memberInitials}
                  style={{
                    display: member.image ? "none" : "flex",
                    backgroundColor: member.tint,
                    color: member.accent,
                  }}
                >
                  {member.initials}
                </div>
                <div
                  className={styles.roleIconBadge}
                  style={{ backgroundColor: member.accent }}
                  title={member.role}
                >
                  <IconComp size={14} color="var(--on-ink)" />
                </div>
              </div>

              <div className={styles.memberInfo}>
                <h3 className={styles.memberName}>{member.name}</h3>
                <div className={styles.memberDegree}>
                  <GraduationCap size={13} />
                  <span>{member.degree}</span>
                </div>
                <div
                  className={styles.memberRoleTag}
                  style={{ backgroundColor: member.tint, color: member.accent }}
                >
                  {member.role}
                </div>
                <p className={styles.memberDescription}>{member.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
