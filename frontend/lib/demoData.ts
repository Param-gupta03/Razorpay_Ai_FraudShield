import { TransactionInput } from '../types';

export interface DemoTransaction extends TransactionInput {
  TransactionID: number;
  TransactionDT: number;
  TransactionAmt: number;
  ProductCD: string;
  card1: number;
  card2: number;
  card6: string;
  P_emaildomain: string;
  expectedProb: number;
  expectedRisk: 'LOW' | 'MEDIUM' | 'HIGH';
  expectedAction: 'APPROVE' | 'REVIEW';
  actualLabel: number;
}

export const DEMO_TRANSACTIONS: DemoTransaction[] = [
  {
    TransactionID: 441478,
    TransactionDT: 11520000,
    TransactionAmt: 13.28,
    ProductCD: "W",
    card1: 9500,
    card2: 321.0,
    card6: "credit",
    P_emaildomain: "gmail.com",
    R_emaildomain: "gmail.com",
    C1: 11.0,
    C4: 3.0,
    C7: 3.0,
    D3: 0.0,
    DeviceInfo: "Windows",
    expectedProb: 0.6121,
    expectedRisk: "HIGH",
    expectedAction: "REVIEW",
    actualLabel: 1
  },
  {
    TransactionID: 443491,
    TransactionDT: 11590000,
    TransactionAmt: 150.00,
    ProductCD: "R",
    card1: 15000,
    card2: 150.0,
    card6: "credit",
    P_emaildomain: "gmail.com",
    R_emaildomain: "gmail.com",
    C1: 24.0,
    C4: 10.0,
    C11: 14.0,
    C13: 1.0,
    id_30: "iOS 11.3.0",
    expectedProb: 0.8732,
    expectedRisk: "HIGH",
    expectedAction: "REVIEW",
    actualLabel: 1
  },
  {
    TransactionID: 437512,
    TransactionDT: 11200000,
    TransactionAmt: 34.00,
    ProductCD: "W",
    card1: 10112,
    card2: 512.0,
    card5: 166.0,
    card6: "debit",
    P_emaildomain: "gmail.com",
    C1: 1.0,
    C11: 1.0,
    C13: 1.0,
    expectedProb: 0.0089,
    expectedRisk: "LOW",
    expectedAction: "APPROVE",
    actualLabel: 0
  },
  {
    TransactionID: 450846,
    TransactionDT: 11800000,
    TransactionAmt: 85.00,
    ProductCD: "W",
    card1: 13926,
    card2: 523.0,
    card3: 185.0,
    card6: "credit",
    P_emaildomain: "hotmail.com",
    R_emaildomain: "hotmail.com",
    C1: 2.0,
    C14: 2.0,
    D13: 63.0,
    id_31: "mobile safari generic",
    expectedProb: 0.0154,
    expectedRisk: "LOW",
    expectedAction: "APPROVE",
    actualLabel: 0
  }
];
