import { z } from "zod";

const userFormSchema = z.object({
  email: z.email(),
  username: z
    .string()
    .min(3, "Username must be at least 3 characters")
    .max(50, "Username must be less than 50 characters")
    .regex(
      /^[a-zA-Z0-9_]+$/,
      "Username can only contain letters, numbers, and underscores",
    ),
  first_name: z
    .string()
    .min(1, "First name is required")
    .max(100, "First name must be less than 100 characters"),
  last_name: z
    .string()
    .min(1, "Last name is required")
    .max(100, "Last name must be less than 100 characters"),
  phone: z
    .string()
    .max(20, "Phone number too long")
    .optional()
    .or(z.literal("")),
  department: z
    .string()
    .max(100, "Department name too long")
    .optional()
    .or(z.literal("")),
  job_title: z
    .string()
    .max(100, "Job title too long")
    .optional()
    .or(z.literal("")),
  is_active: z.boolean(),
  send_welcome_email: z.boolean(),
  role_ids: z.array(z.number()).min(1, "At least one role must be selected"),
});

type UserFormData = z.infer<typeof userFormSchema>;

export { userFormSchema, type UserFormData };
