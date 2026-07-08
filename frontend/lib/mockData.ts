import type { ChatMessage } from '@/hooks/useChat';
import type { DocumentChunk } from '@/lib/api';

export const MOCK_LOGIN_CREDENTIALS = {
  email: 'owner@leaseclear.example',
  password: 'leaseclear',
};

export const MOCK_MESSAGES: ChatMessage[] = [
  { id: 'mock-1', role: 'user', text: 'What happens if I pay rent 5 days late?' },
  {
    id: 'mock-2',
    role: 'assistant',
    text: 'Rent is due on the 1st, with a 5-day grace period [lease §3.2]. After that, a late fee of $75 plus $10/day applies [lease §3.2]. On day 5 you would owe the base late fee only, since it falls within the grace window.',
  },
  { id: 'mock-3', role: 'user', text: 'Can I have a cat? Is there a pet deposit?' },
  {
    id: 'mock-4',
    role: 'assistant',
    text: 'Yes — one cat is allowed with prior written approval [pet-addendum §1]. A separate pet deposit of $350 applies, plus a non-refundable $25/month pet fee [pet-addendum §2].',
  },
  {
    id: 'mock-5',
    role: 'user',
    text: 'What is the security deposit, and when do I get it back after move-out?',
  },
  {
    id: 'mock-6',
    role: 'assistant',
    text: "The security deposit is $2,400, equal to one month's rent [lease §4.1]. Your landlord must return it, minus any lawful deductions, within 21 days of move-out [lease §4.3].",
  },
];

export const MOCK_DOCUMENT_CHUNKS: Record<string, DocumentChunk[]> = {
  lease: [
    {
      chunk_id: 'lease-1',
      clause_number: '1',
      clause_label: 'Term of Lease',
      page_number: 1,
      char_start: 0,
      passage:
        'This lease begins on June 1, 2025 and continues for a fixed term of 12 months, ending May 31, 2026, unless renewed or terminated as provided herein.',
    },
    {
      chunk_id: 'lease-2',
      clause_number: '2',
      clause_label: 'Rent Payment',
      page_number: 1,
      char_start: 820,
      passage:
        'Rent of $2,400 is due on the 1st of each month, payable by ACH transfer or check to the Landlord’s designated account.',
    },
    {
      chunk_id: 'lease-3',
      clause_number: '3.2',
      clause_label: 'Late Fees',
      page_number: 2,
      char_start: 140,
      passage:
        'Tenant is granted a 5-day grace period. If rent remains unpaid after the grace period, a late fee of $75 plus $10 per additional day shall apply until paid in full.',
    },
    {
      chunk_id: 'lease-4',
      clause_number: '4.1',
      clause_label: 'Security Deposit',
      page_number: 2,
      char_start: 960,
      passage:
        'Tenant shall pay a security deposit of $2,400, equal to one month’s rent, prior to occupancy.',
    },
    {
      chunk_id: 'lease-5',
      clause_number: '4.3',
      clause_label: 'Return of Deposit',
      page_number: 3,
      char_start: 80,
      passage:
        'Landlord shall return the security deposit, less any lawful deductions for damage beyond normal wear and tear, within 21 days of move-out.',
    },
    {
      chunk_id: 'lease-6',
      clause_number: null,
      clause_label: null,
      page_number: 5,
      char_start: 1220,
      passage:
        'Either party may terminate this agreement for material breach upon 10 days written notice and a reasonable opportunity to cure.',
    },
  ],
  'pet-addendum': [
    {
      chunk_id: 'pet-1',
      clause_number: '1',
      clause_label: 'Pet Approval',
      page_number: 1,
      char_start: 0,
      passage:
        'Tenant may keep one (1) domestic cat on the premises subject to prior written approval from Landlord.',
    },
    {
      chunk_id: 'pet-2',
      clause_number: '2',
      clause_label: 'Pet Deposit & Fees',
      page_number: 1,
      char_start: 410,
      passage:
        'A pet deposit of $350 is required, along with a non-refundable monthly pet fee of $25.',
    },
  ],
  'move-in-report': [
    {
      chunk_id: 'movein-1',
      clause_number: null,
      clause_label: null,
      page_number: 1,
      char_start: 0,
      passage:
        'Kitchen: appliances in good working condition. Minor scuff noted on cabinet below sink.',
    },
    {
      chunk_id: 'movein-2',
      clause_number: null,
      clause_label: null,
      page_number: 2,
      char_start: 410,
      passage: 'Living room: carpet clean, no stains noted. Two small nail holes in the west wall.',
    },
    {
      chunk_id: 'movein-3',
      clause_number: null,
      clause_label: null,
      page_number: 2,
      char_start: 900,
      passage: 'Bathroom: grout slightly discolored around tub. All fixtures functional.',
    },
  ],
  'renewal-notice-2026': [
    {
      chunk_id: 'renewal-1',
      clause_number: '1',
      clause_label: 'Renewal Terms',
      page_number: 1,
      char_start: 0,
      passage:
        'This notice confirms renewal of the lease for an additional 12-month term beginning June 1, 2026.',
    },
    {
      chunk_id: 'renewal-2',
      clause_number: '2',
      clause_label: 'Rent Adjustment',
      page_number: 1,
      char_start: 340,
      passage:
        'Monthly rent shall increase from $2,400 to $2,500, effective at the start of the renewal term.',
    },
  ],
};
