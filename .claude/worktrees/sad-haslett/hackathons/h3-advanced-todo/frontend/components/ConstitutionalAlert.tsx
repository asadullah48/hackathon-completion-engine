'use client';

/**
 * Constitutional Alert Component.
 * Shows constitutional decision status (blocked/flagged/allowed).
 */

import { AlertCircle, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ConstitutionalDecision } from '@/lib/types';

interface ConstitutionalAlertProps {
  decision: ConstitutionalDecision;
  reason?: string;
  className?: string;
  compact?: boolean;
}

export function ConstitutionalAlert({
  decision,
  reason,
  className,
  compact = false,
}: ConstitutionalAlertProps) {
  if (decision === 'allow') {
    return null;
  }

  const isBlocked = decision === 'block';
  const isFlagged = decision === 'flag';

  const baseStyles = cn(
    'rounded-lg border p-4',
    isBlocked && 'bg-red-50 border-red-300',
    isFlagged && 'bg-amber-50 border-amber-300',
    compact && 'p-3',
    className
  );

  const iconStyles = cn(
    'flex-shrink-0',
    isBlocked && 'text-red-600',
    isFlagged && 'text-amber-600'
  );

  const titleStyles = cn(
    'font-semibold',
    isBlocked && 'text-red-800',
    isFlagged && 'text-amber-800'
  );

  const textStyles = cn(
    'text-sm',
    isBlocked && 'text-red-700',
    isFlagged && 'text-amber-700'
  );

  const Icon = isBlocked ? ShieldAlert : AlertTriangle;

  if (compact) {
    return (
      <div className={baseStyles}>
        <div className="flex items-center gap-2">
          <Icon className={cn(iconStyles, 'h-4 w-4')} />
          <span className={titleStyles}>
            {isBlocked ? 'Blocked' : 'Flagged'}
          </span>
          {reason && (
            <span className={cn(textStyles, 'truncate')}>- {reason}</span>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={baseStyles}>
      <div className="flex gap-3">
        <Icon className={cn(iconStyles, 'h-5 w-5 mt-0.5')} />
        <div className="flex-1">
          <h4 className={titleStyles}>
            {isBlocked ? 'Content Blocked' : 'Content Flagged for Review'}
          </h4>
          <p className={cn(textStyles, 'mt-1')}>
            {isBlocked
              ? 'This content violates our constitutional guidelines and cannot be created.'
              : 'This content has been flagged and will require human review.'}
          </p>
          {reason && (
            <div className={cn(textStyles, 'mt-2 p-2 rounded bg-white/50')}>
              <span className="font-medium">Reason:</span> {reason}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Inline constitutional badge for compact displays.
 */
interface ConstitutionalBadgeProps {
  decision: ConstitutionalDecision;
  className?: string;
}

export function ConstitutionalBadge({
  decision,
  className,
}: ConstitutionalBadgeProps) {
  if (decision === 'allow') {
    return null;
  }

  const isBlocked = decision === 'block';

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
        isBlocked
          ? 'bg-red-100 text-red-700'
          : 'bg-amber-100 text-amber-700',
        className
      )}
    >
      {isBlocked ? (
        <>
          <AlertCircle className="h-3 w-3" />
          Blocked
        </>
      ) : (
        <>
          <AlertTriangle className="h-3 w-3" />
          Flagged
        </>
      )}
    </span>
  );
}

export default ConstitutionalAlert;
