type Props = {
  open: boolean;

  diff: string;

  loading: boolean;

  error: string | null;

  onClose: () => void;
};


export function DiffModal({
  open,
  diff,
  loading,
  error,
  onClose,
}: Props) {
  if (!open) {
    return null;
  }


  return (
    <div
      className="diff-modal-backdrop"
      onClick={onClose}
    >
      <div
        className="diff-modal"
        onClick={(event) =>
          event.stopPropagation()
        }
      >
        <div
          className="diff-modal__header"
        >
          <div>
            <span
              className="eyebrow"
            >
              GIT DIFF
            </span>

            <h3>
              Workspace changes
            </h3>
          </div>

          <button
            type="button"
            onClick={onClose}
          >
            ×
          </button>
        </div>


        <div
          className="diff-modal__body"
        >
          {loading && (
            <p>
              Loading diff...
            </p>
          )}

          {error && (
            <p
              className="workspace-error"
            >
              {error}
            </p>
          )}

          {!loading &&
            !error &&
            !diff.trim() && (
              <p>
                No Git changes.
              </p>
            )}

          {!loading &&
            !error &&
            diff && (
              <pre
                className="git-diff"
              >
                {diff}
              </pre>
            )}
        </div>
      </div>
    </div>
  );
}