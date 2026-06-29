### React Development

* Keep components small and focused. If a component has subcomponents that are only used within it, define them in the same file above it.
* Use Tailwind CSS for styling. Prefer modern utility patterns (`flex`, `grid`, `gap`, `p-*`, `space-*`) over manual spacing or positioning. Prefer gap and padding for spacing layouts over manually adding pb/pt on all children.
* Components with a single expression body should use an implicit return.
* Always use `type` (never `interface`) for custom types, including component props.
* Define all component-specific types at the top of the file, immediately above the component that uses them.
* Prefer named exports. Use default exports only when there is a strong reason.
* Keep internal subcomponents, helper functions, and types unexported unless they are reused elsewhere.

