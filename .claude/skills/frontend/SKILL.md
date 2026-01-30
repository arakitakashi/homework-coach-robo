# Frontend Development - Next.js + TypeScript + React

**Version**: 1.0 | **Last Updated**: 2026-01-31 | **For**: Next.js 14+ App Router

---

## Overview

Best practices for frontend development with Next.js, TypeScript, and React.

**Tech Stack:**
- Next.js 14+ (App Router)
- TypeScript 5+
- React 18+
- Tailwind CSS 3+
- Jotai (State Management)
- Vitest + Testing Library

---

## Quick Start

### Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Route groups
│   ├── session/             # Session pages
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Home page
├── components/              # Reusable components
│   ├── ui/                  # UI primitives
│   ├── features/            # Feature components
│   └── layouts/             # Layout components
├── lib/                     # Utilities
│   ├── atoms/               # Jotai atoms
│   ├── hooks/               # Custom hooks
│   ├── utils/               # Utility functions
│   └── api/                 # API clients
├── types/                   # Type definitions
└── public/                  # Static assets
```

---

## TypeScript Guidelines

### Type Definition Principles

```typescript
// ✅ Good: Explicit type definitions
interface SessionConfig {
  userId: string;
  character: CharacterType;
  gradeLevel: 1 | 2 | 3;
  startTime: Date;
}

function createSession(config: SessionConfig): Session {
  // implementation
}

// ❌ Bad: Using any
function createSession(config: any): any {
  // implementation
}
```

### Type Exports

```typescript
// types/session.ts
export type CharacterType = 'robot' | 'wizard' | 'astronaut' | 'animal';

export interface Session {
  id: string;
  userId: string;
  character: CharacterType;
  status: 'active' | 'paused' | 'completed';
}

export interface DialogueTurn {
  id: string;
  speaker: 'child' | 'ai';
  content: string;
  timestamp: Date;
  emotion?: 'positive' | 'neutral' | 'negative';
}
```

### Utility Types

```typescript
// Derive new types from existing ones
type SessionUpdate = Partial<Session>;
type SessionCreation = Omit<Session, 'id'>;
type SessionId = Pick<Session, 'id'>;
```

---

## React Component Conventions

### Function Components with TypeScript

```typescript
// ✅ Good: Function component with types
interface CharacterAvatarProps {
  character: CharacterType;
  audioLevel: number;
  isRecording: boolean;
}

export function CharacterAvatar({
  character,
  audioLevel,
  isRecording
}: CharacterAvatarProps) {
  return (
    <div className="character-avatar">
      {/* implementation */}
    </div>
  );
}

// ❌ Bad: Class components
export class CharacterAvatar extends React.Component {
  // implementation
}
```

### Server Components vs Client Components

```typescript
// ✅ Server Component (default)
// app/session/[id]/page.tsx
export default async function SessionPage({ params }: { params: { id: string } }) {
  const session = await getSession(params.id);

  return (
    <div>
      <SessionHeader session={session} />
      <DialogueInterface sessionId={params.id} />
    </div>
  );
}

// ✅ Client Component (use 'use client')
// components/features/DialogueInterface.tsx
'use client';

import { useAtom } from 'jotai';
import { isRecordingAtom } from '@/lib/atoms/session';

export function DialogueInterface({ sessionId }: { sessionId: string }) {
  const [isRecording, setIsRecording] = useAtom(isRecordingAtom);

  return (
    <div>
      {/* WebSocket, state management, etc. */}
    </div>
  );
}
```

### Custom Hooks

```typescript
// lib/hooks/useAudioRecorder.ts
import { useAtom } from 'jotai';
import { audioLevelAtom, isRecordingAtom } from '@/lib/atoms/session';
import { useCallback, useEffect, useRef } from 'react';

export function useAudioRecorder() {
  const [audioLevel, setAudioLevel] = useAtom(audioLevelAtom);
  const [isRecording, setIsRecording] = useAtom(isRecordingAtom);
  const streamRef = useRef<MediaStream | null>(null);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      streamRef.current = stream;
      setIsRecording(true);
      monitorAudioLevel(stream, setAudioLevel);
    } catch (error) {
      console.error('Failed to start recording:', error);
      throw error;
    }
  }, [setIsRecording, setAudioLevel]);

  const stopRecording = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsRecording(false);
    setAudioLevel(0);
  }, [setIsRecording, setAudioLevel]);

  return { isRecording, audioLevel, startRecording, stopRecording };
}
```

### Error Handling

```typescript
// Error boundaries
'use client';
import { Component, ReactNode } from 'react';

interface ErrorBoundaryProps { children: ReactNode; fallback?: ReactNode; }

export class ErrorBoundary extends Component<ErrorBoundaryProps, { hasError: boolean }> {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('Error:', error, info);
  }
  render() {
    if (this.state.hasError) return this.props.fallback || <div>Error</div>;
    return this.props.children;
  }
}

// Usage: <ErrorBoundary fallback={<ErrorMessage />}><Component /></ErrorBoundary>
```

---

## Naming Conventions

### Files

```
// ✅ Good
CharacterAvatar.tsx          # Component
useAudioRecorder.ts          # Hook
sessionApi.ts                # API client
formatDuration.ts            # Utility

// ❌ Bad
character-avatar.tsx
use_audio_recorder.ts
SessionAPI.ts
```

### Variables & Functions

```typescript
// ✅ Good: camelCase
const sessionId = 'abc123';
const isRecording = true;
function handleStartRecording() {}

// ❌ Bad
const SessionId = 'abc123';
const is_recording = true;
function HandleStartRecording() {}
```

### Types & Interfaces

```typescript
// ✅ Good: PascalCase
interface SessionConfig {}
type CharacterType = 'robot' | 'wizard';

// ❌ Bad
interface sessionConfig {}
type character_type = 'robot' | 'wizard';
```

---

## Tailwind CSS Guidelines

### Basic Principles

- Use utility-first approach
- Avoid custom CSS when possible
- Use `@apply` sparingly
- Prefer composition over customization

### Component Styling

```typescript
// ✅ Good: Utility classes
export function Button({ children, variant = 'primary' }: ButtonProps) {
  const baseStyles = 'px-4 py-2 rounded-lg font-medium transition-colors';
  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
  };

  return (
    <button className={`${baseStyles} ${variantStyles[variant]}`}>
      {children}
    </button>
  );
}

// ❌ Bad: Custom CSS
export function Button({ children }: ButtonProps) {
  return <button className="custom-button">{children}</button>;
}
```

### Responsive Design

```typescript
<div className="
  grid 
  grid-cols-1 
  sm:grid-cols-2 
  md:grid-cols-3 
  lg:grid-cols-4 
  gap-4
">
  {/* content */}
</div>
```

### Accessibility

```typescript
// ✅ Good: Accessible markup
<button
  aria-label="Start recording"
  aria-pressed={isRecording}
  onClick={handleStartRecording}
  className="focus:outline-none focus:ring-2 focus:ring-blue-500"
>
  <MicrophoneIcon className="w-6 h-6" />
</button>

// ✅ Good: Keyboard navigation
<div
  role="button"
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  {/* content */}
</div>
```

---

## Testing with Vitest

```typescript
// Component test
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

describe('CharacterAvatar', () => {
  it('renders character avatar', () => {
    render(<CharacterAvatar character="robot" audioLevel={0.5} isRecording={false} />);
    expect(screen.getByRole('img')).toBeInTheDocument();
  });
});

// Hook test
import { renderHook, act } from '@testing-library/react';

describe('useAudioRecorder', () => {
  it('starts recording', async () => {
    const { result } = renderHook(() => useAudioRecorder());
    await act(async () => { await result.current.startRecording(); });
    expect(result.current.isRecording).toBe(true);
  });
});
```

---

## Form Validation (Zod)

```typescript
// lib/validation/sessionSchema.ts
import { z } from 'zod';

export const sessionCreationSchema = z.object({
  userId: z.string().min(1, 'User ID is required'),
  character: z.enum(['robot', 'wizard', 'astronaut', 'animal']),
  gradeLevel: z.number().int().min(1).max(3),
});

export type SessionCreationInput = z.infer<typeof sessionCreationSchema>;

// Usage
'use client';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

export function CreateSessionForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<SessionCreationInput>({
    resolver: zodResolver(sessionCreationSchema)
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <select {...register('character')}>
        <option value="robot">Robot</option>
      </select>
      {errors.character && <span>{errors.character.message}</span>}
    </form>
  );
}
```

---

## Best Practices

✅ **Component Design**: Single Responsibility
```typescript
// ✅ Good: Separate concerns
function SessionHeader({ session }: { session: Session }) {
  return <header>{session.id}</header>;
}
function SessionActions({ sessionId }: { sessionId: string }) {
  return <div>{/* actions */}</div>;
}
```

✅ **State Management**: Use Jotai for global state
```typescript
// lib/atoms/session.ts
import { atom } from 'jotai';
export const isRecordingAtom = atom(false);
```

✅ **Performance**: Memoization
```typescript
import { memo, useMemo } from 'react';
export const CharacterAvatar = memo(function CharacterAvatar({ character }: Props) {
  const avatarUrl = useMemo(() => getAvatarUrl(character), [character]);
  return <img src={avatarUrl} />;
});
```

---

## Checklist

### Development
- [ ] TypeScript strict mode enabled
- [ ] No `any` types used
- [ ] Proper error boundaries
- [ ] Accessibility (ARIA labels, keyboard nav)
- [ ] Responsive design (mobile-first)
- [ ] Test coverage > 80%

### Code Review
- [ ] Components follow single responsibility
- [ ] Proper use of Server/Client components
- [ ] Custom hooks for reusable logic
- [ ] Tailwind utilities (not custom CSS)
- [ ] Zod validation for forms
- [ ] Error handling implemented

---

## References

- [Next.js Docs](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Docs](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Vitest](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)

---

**Version 1.0** | **Use with**: `/tdd` for test-driven development
