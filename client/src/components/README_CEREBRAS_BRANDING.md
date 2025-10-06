# Cerebras Branding Implementation

## Overview

The application has been updated to use Cerebras brand colors (orange theme) instead of the previous green theme to properly showcase the Cerebras platform.

## Color Scheme Changes

### Primary Colors
- **Before**: Green theme (`156 72% 60%` - HSL)
- **After**: Cerebras Orange (`15 100% 60%` - HSL, equivalent to `#FF6B35`)

### Updated Components

#### 1. **Core Color System** (`index.css`)
- Updated `--primary` CSS variable to use Cerebras orange
- All primary UI elements now use the orange theme
- Maintains accessibility and contrast ratios

#### 2. **Metrics Display Components**

**Service Type Colors:**
- **STT (Speech-to-Text)**: `bg-orange-100 text-orange-800` (lightest orange)
- **LLM (Language Model)**: `bg-orange-200 text-orange-900` (medium orange)
- **TTS (Text-to-Speech)**: `bg-orange-300 text-orange-900` (darker orange)
- **MCP (Model Context Protocol)**: `bg-orange-400 text-orange-900` (darkest orange)

**Data Value Colors:**
- **Total Messages**: `text-orange-600`
- **Total Response Time**: `text-orange-700`
- **Total Tokens**: `text-orange-800`
- **Average per Message**: `text-orange-900`

#### 3. **Updated Files**
- `client/src/index.css` - Primary color scheme
- `client/src/components/MetricsDisplay.tsx` - Service colors
- `client/src/components/MetricsTable.tsx` - Table colors and service badges
- `client/src/components/ConversationMetricsSummary.tsx` - Card view colors

## Brand Consistency

### Color Hierarchy
The orange theme uses a progressive color scale:
- **Light Orange** (100-200): For backgrounds and subtle elements
- **Medium Orange** (300-400): For service type badges
- **Dark Orange** (600-900): For data values and emphasis

### Dark Mode Support
All color changes include proper dark mode variants:
- Light mode: Orange backgrounds with dark text
- Dark mode: Dark orange backgrounds with light text

## Benefits

- ✅ **Brand Alignment**: Matches Cerebras official branding
- ✅ **Visual Consistency**: Unified orange theme throughout
- ✅ **Accessibility**: Maintains proper contrast ratios
- ✅ **Professional Appearance**: Cohesive color scheme
- ✅ **Dark Mode Compatible**: Works in both light and dark themes

## Technical Implementation

The color scheme uses Tailwind CSS orange color palette:
- `orange-100` through `orange-900` for progressive intensity
- HSL color format for CSS variables (`15 100% 60%`)
- Consistent application across all metrics components

This ensures the application properly represents the Cerebras platform with their signature orange branding.
