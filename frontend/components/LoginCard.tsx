'use client';

import { LogoMark } from '@/components/Logo';
import { Spinner } from '@/components/Spinner';
import { CloseIcon, GoogleIcon } from '@/components/icons';
import { useLogin, type LoginNotice } from '@/hooks/useLogin';
import { useState, type ReactNode } from 'react';

const INPUT_CLASSES =
  'w-full rounded-lg border border-hairline-input bg-bg-inset px-3 py-2.5 text-sm text-text-main outline-none focus:border-white/40 focus:shadow-[0_0_0_3px_rgba(255,255,255,0.12)]';

type FieldProps = {
  label: string;
  children: ReactNode;
};

function Field({ label, children }: FieldProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-text-secondary text-[12.5px] font-medium">{label}</label>
      {children}
    </div>
  );
}

type NoticeProps = {
  notice: LoginNotice;
};

function Notice({ notice }: NoticeProps) {
  const color = notice.kind === 'error' ? 'text-[#e07f84]' : 'text-text-secondary';
  return <div className={`text-[12.5px] ${color}`}>{notice.text}</div>;
}

type LoginCardProps = {
  isDemo?: boolean;
  onClose?: () => void;
};

export function LoginCard({ isDemo = false, onClose }: LoginCardProps = {}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { isSubmitting, notice, submit, googleSignIn, tryDemo } = useLogin(onClose);

  return (
    <div className="border-hairline bg-bg-surface relative w-[380px] max-w-full rounded-xl border px-8 py-9 shadow-[0_8px_30px_rgba(0,0,0,0.35)]">
      {isDemo && onClose && (
        <button
          onClick={onClose}
          className="hover:text-text-main absolute top-4 right-4 flex h-7 w-7 cursor-pointer items-center justify-center rounded-md text-[rgba(236,237,239,0.45)] hover:bg-white/8"
          aria-label="Close"
        >
          <CloseIcon />
        </button>
      )}
      <div className="mb-7 flex flex-col items-center gap-3.5">
        <LogoMark size="login" />
        <div className="text-text-main text-[17px] font-semibold tracking-[-0.01em]">
          LeaseClear
        </div>
      </div>

      <div className="mb-7 text-center text-[13px] leading-normal text-[rgba(236,237,239,0.55)]">
        Sign in to upload your leases
      </div>

      <form
        className="flex flex-col gap-3.5"
        onSubmit={(e) => {
          e.preventDefault();
          submit('login', email, password);
        }}
      >
        <Field label="Email">
          <input
            type="email"
            placeholder="you@example.com"
            className={INPUT_CLASSES}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </Field>
        <Field label="Password">
          <input
            type="password"
            placeholder="••••••••"
            className={INPUT_CLASSES}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </Field>

        <div className="-mt-1.5 flex justify-end">
          <span className="hover:text-text-main cursor-pointer text-[12.5px] whitespace-nowrap text-[rgba(236,237,239,0.55)]">
            Forgot password?
          </span>
        </div>

        {notice && <Notice notice={notice} />}

        <button
          type="submit"
          disabled={isSubmitting}
          className="bg-emphasis text-on-emphasis hover:bg-emphasis-hover mt-1 flex h-10 w-full cursor-pointer items-center justify-center rounded-lg p-[11px] text-sm font-semibold disabled:cursor-default disabled:opacity-70"
        >
          {isSubmitting ? <Spinner size={17} /> : 'Sign in'}
        </button>

        <div className="my-1.5 flex items-center gap-3">
          <div className="bg-hairline h-px flex-1" />
          <div className="text-text-muted text-xs">or</div>
          <div className="bg-hairline h-px flex-1" />
        </div>

        <button
          type="button"
          onClick={googleSignIn}
          disabled={isSubmitting}
          className="border-hairline-input bg-bg-inset text-text-main hover:border-hairline-hover hover:bg-bg-inset-hover flex w-full cursor-pointer items-center justify-center gap-[9px] rounded-lg border p-2.5 text-sm font-medium disabled:cursor-default disabled:opacity-70"
        >
          <GoogleIcon />
          Continue with Google
        </button>
      </form>

      <div className="mt-[22px] text-center text-[12.5px] text-[rgba(236,237,239,0.5)]">
        Don&apos;t have an account?{' '}
        <span
          className="text-text-main hover:text-emphasis-hover cursor-pointer font-medium"
          onClick={() => submit('register', email, password)}
        >
          Sign up
        </span>
        {!isDemo && (
          <>
            {' '}
            or{' '}
            <span
              className="text-text-main hover:text-emphasis-hover cursor-pointer font-medium"
              onClick={tryDemo}
            >
              try demo
            </span>
          </>
        )}
      </div>
    </div>
  );
}
